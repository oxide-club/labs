"""SPDX-License-Identifier: MIT — verificações públicas, sem solução do simulador."""
import re
import subprocess
import sys
from pathlib import Path

CASES = [
    ('vazio', [], (0,0,0)),
    ('isolado', [0], (0,1,0)),
    ('repetido', [0,0], (1,1,0)),
    ('trace A', [0,15,16,64,79,0,31,80], (3,5,3)),
    ('trace B', [0,16,32,48,1,17,33,49,64,80,96,112,0,16,32,48], (4,12,8)),
    ('endereço de 64 bits', [0xffffffffffffffff, 0xfffffffffffffff0], (1,1,0)),
    ('bits acima de 32 bits', [0x100000000, 0x0], (0,2,1)),
    ('contadores hits acima de 255', [0]*300, (299,1,0)),
    ('contadores misses/evictions acima de 255', [0,64]*130, (0,260,259)),
]
def main():
    if len(sys.argv) != 2:
        print('uso: python3 checks/check.py CAMINHO_DO_EXECUTAVEL', file=sys.stderr)
        return 2
    executable = str(Path(sys.argv[1]).resolve())
    failures = 0
    for name, addresses, expected in CASES:
        try:
            run = subprocess.run([executable], input=''.join(f'L 0x{a:X}\n' for a in addresses), text=True, capture_output=True, timeout=5)
            match = re.fullmatch(r'hits=(\d+) misses=(\d+) evictions=(\d+)\n?', run.stdout)
            actual = tuple(map(int, match.groups())) if match else None
            ok = run.returncode == 0 and actual == expected
            print(f'{"OK" if ok else "FALHOU"}: {name}; esperado={expected}; observado={actual}; status={run.returncode}')
            failures += not ok
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f'FALHOU: {name}: {error}')
            failures += 1
    return int(bool(failures))
if __name__ == '__main__':
    sys.exit(main())
