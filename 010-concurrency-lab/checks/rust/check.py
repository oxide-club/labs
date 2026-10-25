# SPDX-License-Identifier: MIT
"""Harness Rust nativo com cargas compartilhadas; sem compilar C."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compile-only', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='oxide-concurrency-rust-') as directory:
        binary = str(Path(directory)/'public')
        subprocess.run(['rustc', '--edition=2021', str(ROOT/'checks/rust/public.rs'),
                        '-o', binary], check=True, timeout=60)
        if args.compile_only:
            print('Preparação: harness Rust compila; mecanismo ainda incompleto.')
            return 0
        cases = [[name] for name in ('invalid', 'mutex', 'atomic', 'fifo', 'empty',
                                     'full', 'close-empty', 'close-full', 'ordered')]
        for case in json.loads((ROOT/'materials/cases.json').read_text())['queue_cases']:
            cases.append(['stress', *(str(case[key]) for key in
                          ('capacity', 'producers', 'consumers', 'items_per_producer'))])
        failures = 0
        for case in cases:
            try:
                result = subprocess.run([binary, *case], text=True, capture_output=True, timeout=10)
                ok = result.returncode == 0 and result.stdout.strip() == 'PASS'
                print(('PASS ' if ok else 'FAIL ')+' '.join(case))
                if not ok:
                    print(result.stderr)
            except subprocess.TimeoutExpired:
                ok = False
                print('FAIL timeout: '+' '.join(case))
            failures += not ok
        print(f'{len(cases)-failures}/{len(cases)} checks Rust passaram')
        return int(failures != 0)


if __name__ == '__main__':
    raise SystemExit(main())
