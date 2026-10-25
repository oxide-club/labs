# SPDX-License-Identifier: MIT
"""Oráculo Python independente e checks de suporte ou execução GPU real."""
import argparse
import csv
import io
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CASES = [(0, 0), (1, 0), (3, 1000), (63, 1), (64, 2), (65, 3),
         (127, 11), (128, 12), (129, 13), (255, 4), (256, 5), (257, 6),
         (511, 7), (512, 8), (513, 9), (65537, 17), (4194305, 29)]

def expected(n, seed):
    a = [(17*i + seed) % 2049 - 1024 for i in range(n)]
    b = [(31*i + 3*seed) % 2049 - 1024 for i in range(n)]
    return sum(a), [x+y for x, y in zip(a, b)]

def run(args):
    return subprocess.run([str(x) for x in args], capture_output=True, text=True, timeout=120)

def cpu():
    extremes = run([ROOT/'materials/build/oracle-check'])
    assert extremes.returncode == 0, extremes.stderr
    print(extremes.stdout.strip())
    for n, seed in CASES:
        result = run([ROOT/'materials/build/cpu', n, seed])
        assert result.returncode == 0, result.stderr
        values = list(map(int, result.stdout.split()))
        total, vector = expected(n, seed)
        assert values == [total, *vector], (n, seed)
    for n, seed in [('-1', 0), (4194306, 0), ('oops', 0), (1, -1), (1, 1001), ('9'*50, 0)]:
        assert run([ROOT/'materials/build/cpu', n, seed]).returncode == 2
    for mode, sign in [('positive', 1), ('negative', -1)]:
        for n in [0, 1, 65, 4194305]:
            result = run([ROOT/'materials/build/cpu', n, 0, mode])
            assert result.returncode == 0, result.stderr
            values = list(map(int, result.stdout.split()))
            assert values[0] == sign * n * 1024
            assert len(values) == n + 1 and all(x == sign * 2048 for x in values[1:])
            if n == 4194305:
                assert values[0] == sign * 4294968320
    ramp = run([ROOT/'materials/build/cpu', 4194305, 0, 'ramp'])
    assert ramp.returncode == 0, ramp.stderr
    values = list(map(int, ramp.stdout.split()))
    assert values[0] == 4282385411 and values[1:] == [2*(1024-i%7) for i in range(4194305)]
    assert run([ROOT/'materials/build/cpu', 1, 0, 'invalid']).returncode == 2
    print('CPU: modos constantes, 8 casos e rejeição de modo passaram.')
    print('CPU: 17 casos e 6 rejeições passaram; nenhuma execução GPU.')

def gpu():
    for block in [64, 128, 256, 512]:
        for n, seed in CASES:
            result = run([ROOT/'materials/build/gpu', n, block, seed])
            assert result.returncode == 0, (n, block, result.stderr)
            rows = list(csv.DictReader(io.StringIO(result.stdout)))
            assert len(rows) == 1 and int(rows[0]['n']) == n
            for key in ['kernel_ms', 'h2d_ms', 'd2h_ms', 'total_ms']:
                assert float(rows[0][key]) >= 0
    for block in [64, 128, 256, 512]:
        for mode in ['positive', 'negative', 'ramp']:
            result = run([ROOT/'materials/build/gpu', 4194305, block, 0, mode])
            assert result.returncode == 0, (block, mode, result.stderr)
            rows = list(csv.DictReader(io.StringIO(result.stdout)))
            assert len(rows) == 1 and int(rows[0]['n']) == 4194305
    assert run([ROOT/'materials/build/gpu', 1, 64, 0, 'invalid']).returncode == 2
    for args in [(-1, 64, 0), (4194306, 64, 0), (1, 63, 0), (1, 1024, 0), (1, 64, 1001)]:
        assert run([ROOT/'materials/build/gpu', *args]).returncode == 2
    print('GPU: casos públicos passaram, incluindo caudas e rejeições.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', action='store_true')
    args = parser.parse_args()
    gpu() if args.gpu else cpu()
