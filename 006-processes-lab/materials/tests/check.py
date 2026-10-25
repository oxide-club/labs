# SPDX-License-Identifier: MIT
"""Checks públicos Linux/POSIX. Cada execução ocupa uma sessão própria."""
import argparse
import os
from pathlib import Path
import signal
import shutil
import sys
import subprocess
import tempfile
import time
import unittest

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--oxrun', required=True)
PARSER.add_argument('--probe', required=True)
ARGS = PARSER.parse_args()
OXRUN = str(Path(ARGS.oxrun).resolve())
PROBE = str(Path(ARGS.probe).resolve())
FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures'


def preflight():
    missing = [name for name in ("printf", "wc", "dd", "true", "cat", "sh", "sleep")
               if shutil.which(name) is None]
    if missing:
        print("infraestrutura: comandos ausentes no PATH: " + ", ".join(missing),
              file=sys.stderr)
        return False
    for name, path in (("oxrun", OXRUN), ("probe", PROBE)):
        if not Path(path).is_file() or not os.access(path, os.X_OK):
            print(f"infraestrutura: {name} não é arquivo executável: {path}",
                  file=sys.stderr)
            return False
    return True


def execute(arguments):
    process = subprocess.Popen([OXRUN, *arguments], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = process.communicate(timeout=5)
        return process.returncode, out, err
    finally:
        # O PID é também o grupo recém-criado. Nunca procurar processos por nome.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate(timeout=5)


class Contract(unittest.TestCase):
    def expect(self, args, status, output=None, diagnostic=False):
        try:
            code, out, err = execute(args)
        except subprocess.TimeoutExpired:
            self.fail("timeout de 5 s: verifique fechamento dos pipes e ordem dos waits")
        self.assertEqual(code, status, (args, out, err))
        if output is not None:
            self.assertEqual(out, output)
        if diagnostic:
            self.assertTrue(err)
        return out

    def test_argv(self):
        self.expect(['run', '--', 'printf', '%s\n', 'a b'], 0,
                    (FIXTURES / 'argv.txt').read_bytes())
        self.expect(['run', '--', 'printf', '<%s>\n', '', 'x y', ':::'], 0,
                    b'<>\n<x y>\n<:::>\n')

    def test_status(self):
        self.expect(['run', '--', PROBE], 7)
        self.expect(['run', '--', PROBE, 'signal'], 143)
        with tempfile.TemporaryDirectory() as directory:
            absent = str(Path(directory) / 'nao-existe-oxide')
            self.expect(['run', '--', absent], 127, diagnostic=True)
            blocked = Path(directory) / 'not-executable'
            blocked.write_bytes((FIXTURES / 'not-executable.txt').read_bytes())
            blocked.chmod(0o600)
            self.expect(['run', '--', str(blocked)], 126, diagnostic=True)

    def test_pipe(self):
        out = self.expect(['pipe', '--', 'printf', 'abc\n', ':::', 'wc', '-c'], 0)
        self.assertEqual(int(out), 4)
        out = self.expect(['pipe', '--', 'dd', 'if=/dev/zero', 'bs=1024',
                           'count=1024', ':::', 'wc', '-c'], 0)
        self.assertEqual(int(out), 1048576)
        self.expect(['pipe', '--', 'true', ':::', 'cat'], 0, b'')
        self.expect(['pipe', '--', PROBE, ':::', 'true'], 0)
        self.expect(['pipe', '--', 'true', ':::', PROBE], 7)

    def test_reap_both_children(self):
        for _ in range(3):
            start = time.monotonic()
            self.expect(['pipe', '--', 'sh', '-c',
                         'exec 1>&- 2>&-; sleep 0.4; exit 7', ':::', 'true'], 0, b'')
            self.assertGreaterEqual(time.monotonic() - start, 0.3,
                                    'oxrun retornou antes do término do filho esquerdo')

    def test_invalid(self):
        for args in ([], ['run'], ['run', '--'], ['run', 'true'],
                     ['unknown', '--', 'true'], ['pipe', '--', 'true'],
                     ['pipe', '--', ':::', 'true'],
                     ['pipe', '--', 'true', ':::'],
                     ['pipe', '--', 'true', ':::', 'true', ':::', 'true']):
            with self.subTest(args=args):
                self.expect(args, 2, diagnostic=True)
        # A ausência de fork/exec antes da validação exige revisão do código.



if __name__ == '__main__':
    if not preflight():
        sys.exit(3)
    unittest.main(argv=['check.py'])
