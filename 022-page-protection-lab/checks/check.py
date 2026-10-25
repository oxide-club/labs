#!/usr/bin/env python3
# SPDX-License-Identifier: MIT — Oxide Club, 2026.
"""Checks comportamentais; não substituem revisão do supervisor e traces."""
import argparse
import json
import math
import os
import signal
import subprocess
import sys
import tempfile
from audit_trace import Unavailable, collect
from pathlib import Path

IDS = ['none-read', 'none-write', 'r-read', 'r-write', 'w-read', 'w-write',
       'rw-read', 'rw-write', 'transition', 'unaligned', 'zero-length', 'hang', 'continuity']
PROTECTION = ['NONE', 'NONE', 'R', 'R', 'W', 'W', 'RW', 'RW', 'RW-R-RW', 'R', 'RW', 'RW', 'RW']

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def run(binary, args):
    # Grupo próprio permite encerrar descendentes de um supervisor defeituoso.
    p = subprocess.Popen([binary, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    try:
        out, err = p.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        raise AssertionError('prazo externo excedido; grupo encerrado')
    remaining = False
    try:
        os.killpg(p.pid, 0)
        remaining = True
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    require(not remaining, 'processos remanescentes no grupo após saída do supervisor')
    print(json.dumps({'args': args, 'returncode': p.returncode, 'stdout': out, 'stderr': err}))
    return p.returncode, out

def rows(out):
    return [json.loads(line) for line in out.splitlines()]

def check_record(r, limit):
    name = r['id']
    require(name in IDS, 'ID desconhecido')
    prefix = name + ': '
    def check(ok, msg):
        require(ok, prefix + msg)
    check(r['protection'] == PROTECTION[IDS.index(name)], 'proteção solicitada')
    check(r['reaped'] is True, 'child reaping ausente')
    check(type(r['pid']) is int and r['pid'] > 0, 'PID ausente')
    check(type(r['page_size']) is int and r['page_size'] > 0 and r['pages'] == 3, 'região')
    check(isinstance(r['duration_ms'], (int, float)) and math.isfinite(r['duration_ms'])
          and r['duration_ms'] >= 0, 'duração inválida')
    check(r['result'] in ['ok', 'signal', 'setup_error', 'timeout', 'unsupported'], 'resultado')
    for field in ['exit_code', 'signal', 'errno', 'byte']:
        check(type(r[field]) is int, field + ' deve ser inteiro')
    check(isinstance(r['detail'], str), 'detalhe ausente')
    check('x' not in r['permissions'], 'execução implícita: ambiente incompatível')
    if name in ['unaligned', 'zero-length']:
        check(r['operation'] == 'setup' and r['result'] == 'setup_error', 'erro intencional')
        check(r['errno'] == 22 and r['signal'] == 0 and r['exit_code'] == 2, 'EINVAL separado do sinal')
        check(r['byte'] == -1, 'acesso após erro de preparação')
        return
    check(len(r['permissions']) == 4 and r['permissions'][3] == 'p', 'mapeamento privado')
    if name == 'hang':
        check(r['operation'] == 'wait' and r['result'] == 'timeout', 'timeout não é SIGSEGV')
        check(limit <= r['duration_ms'] <= limit + 1500, 'prazo fora da tolerância de 1500 ms')
        check(r['signal'] == signal.SIGKILL and r['exit_code'] == -1, 'encerrar e coletar status')
        return
    check(r['errno'] == 0, 'erro inesperado de preparação')
    if name in ['none-read', 'none-write', 'r-write'] or (name == 'w-read' and r['result'] == 'signal'):
        check(r['result'] == 'signal' and r['signal'] == signal.SIGSEGV and r['exit_code'] == -1,
              'SIGSEGV real obrigatório')
    else:
        check(r['result'] == 'ok' and r['exit_code'] == 0 and r['signal'] == 0, 'sucesso obrigatório')
        check(r['byte'] == (90 if name in ['w-write', 'rw-write', 'transition'] else 165), 'byte incorreto')
    check(r['operation'] == ('transition' if name == 'transition' else 'write' if name.endswith('write') else 'read'), 'operação')
    if name == 'transition':
        check(r['detail'] == '165,165,90', 'preservação/restauração RW-R-RW')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('binary', type=lambda s: str(Path(s).resolve()))
    ap.add_argument('--audit-out', type=Path, help='diretório novo para registros independentes de strace')
    args = ap.parse_args()
    code, out = run(args.binary, ['--case', 'all', '--timeout-ms', '200'])
    rs = rows(out)
    if any(r.get('result') == 'unsupported' for r in rs):
        require(code == 2, 'unsupported exige saída 2')
        print('NÃO EXECUTADO: ambiente incompatível', file=sys.stderr)
        return 2
    # Conferir a causa antes do status global ajuda a diagnosticar mutantes.
    require([r['id'] for r in rs] == IDS, 'matriz incompleta ou ordem sem continuidade')
    for r in rs:
        check_record(r, 200)
    require(code == 0, 'all: erros INTENCIONAIS conferidos exigem saída 0')
    for name in IDS:
        code, out = run(args.binary, ['--case', name, '--timeout-ms', '100'])
        rs = rows(out)
        require(len(rs) == 1 and rs[0]['id'] == name, 'seleção do caso')
        check_record(rs[0], 100)
        require(code == 0, name + ': retorno agregado')
    for invalid in [['--case', 'missing'], ['--timeout-ms', '99'], ['--timeout-ms', '10001'],
                    ['--timeout-ms', 'x'], ['--timeout-ms', '100x'], ['--case'], ['--unknown'],
                    ['--case', 'all', '--case', 'r-read']]:
        code, out = run(args.binary, invalid)
        require(code == 2 and not out, 'argumentos inválidos: saída 2 sem sondas')
    if args.audit_out:
        collect(args.binary, args.audit_out)
    else:
        with tempfile.TemporaryDirectory(prefix='pageprobe-audit-') as folder:
            collect(args.binary, Path(folder)/'trace')
    print('APROVADO: comportamento e terminação real conferidos por strace')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Unavailable as e:
        print('NÃO EXECUTADO: ' + str(e), file=sys.stderr)
        sys.exit(2)
    except (AssertionError, KeyError, ValueError, OSError) as e:
        print('FALHOU: ' + str(e), file=sys.stderr)
        sys.exit(1)
