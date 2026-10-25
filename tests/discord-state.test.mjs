import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readState, updateState } from '../scripts/discord/state.mjs';
const empty = () => ({
  version: 1,
  initialized: false,
  records: {},
  revisions: {},
});
const error = (status) => Object.assign(new Error('HTTP'), { status });
test('absent state is distinct from permission and invalid data errors', async () => {
  assert.equal(
    (
      await readState(
        {
          github: async () => {
            throw error(404);
          },
        },
        'oxide-club/labs',
      )
    ).sha,
    null,
  );
  await assert.rejects(
    readState(
      {
        github: async () => {
          throw error(403);
        },
      },
      'oxide-club/labs',
    ),
  );
  for (const data of [
    {},
    { ...empty(), version: 2 },
    { ...empty(), records: [] },
  ]) {
    await assert.rejects(
      readState(
        {
          github: async () => ({
            encoding: 'base64',
            sha: 'abc',
            content: Buffer.from(JSON.stringify(data)).toString('base64'),
          }),
        },
        'oxide-club/labs',
      ),
      /state/,
    );
  }
});
test('conditional conflict preserves another PR and retries mutation without side effects', async () => {
  let value = empty();
  let sha = 'one';
  let puts = 0;
  const client = {
    github: async (path, options = {}) => {
      assert.match(path, /^\/repos\/oxide-club\/labs\//);
      if (options.method === 'PUT') {
        puts++;
        if (puts === 1) {
          value.records['pr:2'] = { url: 'other' };
          sha = 'two';
          throw error(409);
        }
        assert.equal(options.body.sha, 'two');
        value = JSON.parse(
          Buffer.from(options.body.content, 'base64').toString(),
        );
        return {};
      }
      return {
        encoding: 'base64',
        content: Buffer.from(JSON.stringify(value)).toString('base64'),
        sha,
      };
    },
  };
  await updateState(client, 'oxide-club/labs', (state) => {
    state.records['pr:1'] = { url: 'first' };
  });
  assert.deepEqual(Object.keys(value.records).sort(), ['pr:1', 'pr:2']);
});
test('creates an orphan state branch and handles a concurrent creator', async () => {
  let created = false;
  const calls = [];
  const client = {
    github: async (path, options = {}) => {
      calls.push([path, options]);
      if (path.includes('/contents/')) {
        if (!created) throw error(404);
        return {
          encoding: 'base64',
          sha: 'blob',
          content: Buffer.from(JSON.stringify(empty())).toString('base64'),
        };
      }
      if (path.endsWith('/git/ref/heads/discord-state')) {
        if (!created) throw error(404);
        return { object: { sha: 'commit' } };
      }
      if (path.endsWith('/git/refs')) {
        created = true;
        throw error(422);
      }
      return { sha: 'abc' };
    },
  };
  await updateState(client, 'oxide-club/labs', (state) => {
    state.initialized = true;
  });
  const commit = calls.find(([path]) => path.endsWith('/git/commits'));
  assert.deepEqual(commit[1].body.parents, []);
  assert.equal(calls.at(-1)[1].body.branch, 'discord-state');
});

test('labs recovery CLI records or releases a pending PR without a webhook', async () => {
  const { spawnSync } = await import('node:child_process');
  const preload = `
    globalThis.fetch = async (url, options) => {
      if (!url.startsWith('https://api.github.com/repos/oxide-club/labs/'))
        throw new Error('Unexpected destination');
      if (options.method === 'PUT') {
        const body = JSON.parse(options.body);
        console.log(Buffer.from(body.content, 'base64').toString());
        return Response.json({});
      }
      if (url.endsWith('/git/ref/heads/discord-state'))
        return Response.json({ object: { sha: 'commit' } });
      return Response.json({
        encoding: 'base64', sha: 'blob',
        content: Buffer.from(JSON.stringify({
          version: 1, initialized: false, revisions: {},
          records: { 'pr:42': { url: 'https://github.com/oxide-club/labs/pull/42', pending: true } }
        })).toString('base64')
      });
    };
  `;
  for (const mode of ['record', 'release']) {
    const result = spawnSync(process.execPath, [
      '--import', `data:text/javascript,${encodeURIComponent(preload)}`,
      'scripts/discord/state.mjs', mode, 'pr:42', ...(mode === 'record' ? ['1234'] : []),
    ], {
      cwd: new URL('..', import.meta.url),
      env: { ...process.env, GITHUB_REPOSITORY: 'oxide-club/labs', GH_TOKEN: 'fixture' },
      encoding: 'utf8',
    });
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr);
    const state = JSON.parse(result.stdout);
    if (mode === 'record') {
      assert.equal(state.records['pr:42'].messageId, '1234');
      assert.equal(state.records['pr:42'].pending, undefined);
    } else {
      assert.deepEqual(state.records, {});
    }
  }
});
