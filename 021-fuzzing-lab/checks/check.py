#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Preparação anterior à campanha; não é check de conclusão do parser."""
import argparse
import os
from pathlib import Path
import subprocess

# Resultados literais calculados sem executar o parser.
CASES = [
    ('empty', '4f58463100000000', 'Ok 0 0 0'),
    ('checksum', '4f584631010000000000', 'Ok 1 0 0'),
    ('number', '4f5846310001040001020100', 'Ok 0 1 1 1:0100'),
    ('text', '4f5846310001040002024f4b', 'Ok 0 0 1 2:4f4b'),
    ('empty-text', '4f584631000102000200', 'Ok 0 0 1 2:'),
    ('header', '4f58', 'Truncated'),
    ('magic', '4e4f504500000000', 'BadMagic'),
    ('flags', '4f58463102000000', 'BadFlags'),
]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('runner'); ap.add_argument('--smoke', action='store_true', help='Alias compatível: todos os casos são de preparação.')
    a=ap.parse_args()
    env=dict(os.environ, ASAN_OPTIONS=os.environ.get('ASAN_OPTIONS','detect_leaks=1:abort_on_error=1'), UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    cases=CASES+[CASES[0], CASES[3], CASES[0],('null','','Truncated'),CASES[3]]
    try:
        result=subprocess.run([str(Path(a.runner).resolve())], input=''.join(data+'\n' for _,data,_ in cases), text=True, capture_output=True, timeout=2, env=env)
    except (OSError,subprocess.TimeoutExpired) as error:
        print(f'PREPARATION_UNAVAILABLE {type(error).__name__}'); return 2
    if 'LeakSanitizer has encountered a fatal error' in result.stderr:
        print('PREPARATION_UNAVAILABLE: LeakSanitizer não inicializou neste contexto; teste fora do debugger/sandbox e registre a limitação.'); return 2
    if result.returncode or result.stdout.splitlines()!=[want for _,_,want in cases]:
        print(f'PREPARATION_FAILED exit={result.returncode}; confira toolchain e runner. Nenhuma conclusão sobre os dois defeitos.'); return 1
    print('PREPARATION_OK cases=8 interleaved=5; regressões completas somente após registrar a campanha.')
    return 0
if __name__=='__main__': raise SystemExit(main())
