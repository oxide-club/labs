#!/usr/bin/env python3
# SPDX-License-Identifier: MIT — Oxide Club, 2026.
"""Confronta JSONL com terminação e wait4 observados por strace próprio."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys


class Unavailable(RuntimeError):
    """Instrumento indisponível; não constitui aprovação."""


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def events(trace):
    """Reúne syscalls interrupted/resumed por PID, sem confundir sinal com saída."""
    pending = {}
    result = []
    for line in trace.splitlines():
        match = re.match(r'^(\d+)\s+(.*)$', line)
        if not match:
            continue
        pid, body = int(match[1]), match[2]
        if body.endswith('<unfinished ...>'):
            pending[pid] = body.removesuffix('<unfinished ...>')
            continue
        resumed = re.match(r'^<\.\.\. \w+ resumed>(.*)$', body)
        if resumed:
            need(pid in pending, 'trace incompleto: retomada sem início')
            body = pending.pop(pid) + resumed[1]
        result.append((pid, re.sub(r'\s+', ' ', body).replace(' )', ')')))
    return result


def audit(trace, records):
    from check import IDS, check_record
    need([r['id'] for r in records] == IDS, 'auditoria requer all completo e ordenado')
    for record in records:
        check_record(record, 200)
    rows = events(trace)
    pids = [r['pid'] for r in records]
    need(len(set(pids)) == 13, 'cada caso exige filho novo')
    spawned = {}
    for owner, body in rows:
        if re.match(r'^(clone|clone3|fork|vfork)\(', body):
            match = re.search(r' = (\d+)$', body)
            if match and int(match[1]) > 0:
                spawned[int(match[1])] = owner
    need(set(spawned) == set(pids), 'filhos do trace diferem dos 13 registros')
    need(len(set(spawned.values())) == 1, 'sondas devem ser filhos do supervisor')
    parent = next(iter(spawned.values()))
    for r in records:
        name, pid = r['id'], r['pid']
        own = [body for owner, body in rows if owner == pid]
        final = [body for body in own if body.startswith('+++ ')]
        segv = name in ['none-read', 'none-write', 'r-write'] or (name == 'w-read' and r['result'] == 'signal')
        if segv or name == 'hang':
            sig = 'SIGSEGV' if segv else 'SIGKILL'
            terminal = rf'\+\+\+ killed by {sig}(?: \(core dumped\))? \+\+\+'
            wait_status = f'WIFSIGNALED(s) && WTERMSIG(s) == {sig}'
        else:
            code = 2 if name in ['unaligned', 'zero-length'] else 0
            terminal = rf'\+\+\+ exited with {code} \+\+\+'
            wait_status = f'WIFEXITED(s) && WEXITSTATUS(s) == {code}'
        need(len(final) == 1 and re.fullmatch(terminal, final[0]) is not None,
             f'{name}: terminação real diverge: {final}; esperado {terminal}')
        waits = [body for owner, body in rows if owner == parent and body.startswith('wait4(')
                 and body.endswith(' = ' + str(pid))]
        need(len(waits) == 1 and wait_status in waits[0], f'{name}: status real de wait4 divergente/ausente')
        if segv:
            need(any('SIGSEGV' in body and 'SEGV_ACCERR' in body for body in own), f'{name}: falta SEGV_ACCERR')
        if name == 'hang':
            need(any(owner == parent and body == f'kill({pid}, SIGKILL) = 0'
                     for owner, body in rows), 'hang: falta kill(SIGKILL) confirmado')
        if name == 'zero-length':
            need(any(re.match(r'^mmap\([^,]+, 0, ', body) is not None and '= -1 EINVAL' in body
                     for body in own), 'zero-length: falta mmap inválido/EINVAL real')
        else:
            page = r['page_size']
            regions = [re.search(r'mmap\([^,]+, ' + str(3*page) +
                                 r', PROT_READ\|PROT_WRITE, MAP_PRIVATE\|MAP_ANONYMOUS, -1, 0\) = (0x[0-9a-f]+)$', body)
                       for body in own]
            regions = [match for match in regions if match]
            need(len(regions) == 1, f'{name}: falta região nova de três páginas inicializada como RW')
            center = int(regions[0][1], 16) + page
            changes = [body for body in own if body.startswith(f'mprotect({hex(center)}, {page}, ')]
            protections = [body.split(', ', 2)[2].split(')')[0] for body in changes if body.endswith(' = 0')]
            if name == 'unaligned':
                need(any(body.startswith(f'mprotect({hex(center+1)}, {page}, ') and '= -1 EINVAL' in body
                         for body in own), 'unaligned: falta mprotect desalinhado/EINVAL real')
            elif name == 'transition':
                need(protections == ['PROT_READ|PROT_WRITE', 'PROT_READ', 'PROT_READ|PROT_WRITE'],
                     'transition: sequência real RW-R-RW divergente')
            else:
                wanted = {'NONE': 'PROT_NONE', 'R': 'PROT_READ', 'W': 'PROT_WRITE', 'RW': 'PROT_READ|PROT_WRITE'}[r['protection']]
                need(protections and protections[0] == wanted, f'{name}: proteção central real divergente')
                if name == 'w-write':
                    need(len(protections) >= 2 and protections[-1] in ['PROT_READ', 'PROT_READ|PROT_WRITE'],
                         'w-write: restauração de leitura ausente no trace')
        need(not any('PROT_EXEC' in body for body in own), f'{name}: filho solicitou execução')
        print(f'{name}: terminação e wait4 reais conferidos')
    need((parent, '+++ exited with 0 +++') in rows, 'supervisor não terminou com 0')
    print('APROVADO: 13 terminações reais e 13 status de espera; entrega de sinal não foi usada como terminação')


def capture(command, prefix):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True, env={**os.environ, 'LC_ALL': 'C'})
    try:
        out, err = p.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        raise AssertionError('prazo externo da auditoria excedido; grupo encerrado')
    remaining = False
    try:
        os.killpg(p.pid, 0)
        remaining = True
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    prefix.with_suffix('.stdout').write_text(out)
    prefix.with_suffix('.stderr').write_text(err)
    prefix.with_suffix('.command.json').write_text(json.dumps({'command': command, 'returncode': p.returncode})+'\n')
    need(not remaining, 'auditoria: processos remanescentes no grupo após supervisor')
    return p.returncode, out, err


def collect(binary, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    strace = shutil.which('strace')
    if not strace:
        raise Unavailable('strace não instalado')
    prefix = directory / 'preflight'
    code, _, err = capture([strace, '-f', '-o', str(directory/'preflight.trace'), '/bin/true'], prefix)
    if code:
        raise Unavailable('ptrace/strace indisponível no teste independente: ' + err.strip())
    tracefile = directory/'all.strace'
    command = [strace, '-f', '-e', 'trace=mmap,mprotect,munmap,clone,clone3,fork,vfork,wait4,kill,close',
               '-o', str(tracefile), str(Path(binary).resolve()), '--case', 'all', '--timeout-ms', '200']
    code, out, err = capture(command, directory/'all')
    records = [json.loads(line) for line in out.splitlines()]
    if any(r.get('result') == 'unsupported' for r in records):
        need(code == 2, 'unsupported deve retornar 2')
        raise Unavailable('supervisor classificou ambiente incompatível')
    need(code == 0, f'auditoria: supervisor retornou {code}: {err.strip()}')
    audit(tracefile.read_text(), records)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--trace', type=Path)
    parser.add_argument('--records', type=Path)
    args = parser.parse_args()
    if args.binary and args.out and not args.trace and not args.records:
        collect(args.binary, args.out)
    elif args.trace and args.records and not args.binary and not args.out:
        audit(args.trace.read_text(), [json.loads(s) for s in args.records.read_text().splitlines()])
    else:
        parser.error('use --binary BIN --out DIRETÓRIO_NOVO ou --trace TRACE --records JSONL')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Unavailable as error:
        print('NÃO EXECUTADO: ' + str(error), file=sys.stderr)
        sys.exit(2)
    except (AssertionError, ValueError, KeyError, OSError) as error:
        print('FALHOU: ' + str(error), file=sys.stderr)
        sys.exit(1)
