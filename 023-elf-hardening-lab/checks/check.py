# SPDX-License-Identifier: MIT
import argparse
import importlib.util
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collector', ROOT/'experiments/run.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    # Independent literal arithmetic: empty=0; A=65; Oxide=79+120+105+100+101=505.
    for profile in 'ABCDEF':
        binary = out/profile
        for value, expected in [('', 'sum=0\n'), ('A', 'sum=65\n'), ('Oxide', 'sum=505\n')]:
            actual = collector.run([str(binary), value])
            if actual != expected:
                raise ValueError(f'{profile}: caso {value!r}: {actual!r}')
        rejected = subprocess.run([str(binary), 'x'*64], capture_output=True, timeout=10)
        if rejected.returncode != 2:
            raise ValueError('limite de entrada não rejeitado')
    raw = collector.run([str(out/'A'), '--maps'])
    collector.parse_maps(raw, out/'A')
    negatives = [raw.replace('ANCHOR stack ', 'MISSING stack '),
                 raw.replace('[stack]', '[wrong]'),
                 raw.replace('libc.so.6', 'wrong-lib.so'),
                 raw.replace(str(out/'A'), str(out/'wrong')),
                 raw.split('MAPS\n')[0]+'MAPS\n']
    for i, broken in enumerate(negatives, 1):
        try:
            collector.parse_maps(broken, out/'A')
        except ValueError as error:
            print(f'controle negativo {i}: rejeitado: {error}')
        else:
            raise ValueError(f'controle negativo {i}: aceito incorretamente')
    print('18 casos funcionais, 6 limites e 5 controles negativos aprovados')

if __name__ == '__main__':
    main()
