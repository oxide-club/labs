# SPDX-License-Identifier: MIT
"""Execute cada grupo Go em processo próprio; fixtures continuam compartilhados."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TESTS = ('TestFixtures', 'TestVectorsAndPartitions', 'TestErrorsAndCompleted',
         'TestLimitsOwnershipAndConcatenation', 'TestPartialChunkOwnership')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compile-only', action='store_true')
    parser.add_argument('--fixture-only', action='store_true')
    parser.add_argument('--race', action='store_true')
    args = parser.parse_args()
    source = ROOT/'materials/starter/go'
    with tempfile.TemporaryDirectory(prefix='oxide-protocol-go-') as directory:
        binary = str(Path(directory)/'protocol-tests')
        env = os.environ.copy()
        env.setdefault('GOCACHE', str(Path(directory)/'cache'))
        env['GOTOOLCHAIN'] = 'local'
        command = ['go', 'test', '-c', '-o', binary]
        if args.race:
            command.append('-race')
        subprocess.run([*command, '.'], cwd=source, env=env, timeout=120, check=True)
        if args.compile_only:
            print('Preparação: Go compila; parser ainda incompleto.')
            return 0
        names = TESTS[:1] if args.fixture_only else TESTS
        failures = 0
        for name in names:
            try:
                result = subprocess.run([binary, '-test.run', '^'+name+'$', '-test.timeout=30s'],
                                        cwd=source, capture_output=True, text=True, timeout=35)
                ok = result.returncode == 0
                print(('PASS ' if ok else 'FAIL ')+name)
                if not ok:
                    print(result.stdout+result.stderr)
            except subprocess.TimeoutExpired:
                ok = False
                print('FAIL timeout: '+name)
            failures += not ok
        print(f'{len(names)-failures}/{len(names)} grupos Go passaram')
        return int(failures != 0)


if __name__ == '__main__':
    raise SystemExit(main())
