# SPDX-License-Identifier: MIT
"""Só mede depois de a suíte GPU passar; CSV contém somente observações reais."""
import csv
import io
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT/'checks/check.py'), '--gpu'], check=True, stdout=sys.stderr)
writer = csv.writer(sys.stdout)
writer.writerow(['size','repeat','n','block','seed','kernel_ms','h2d_ms','d2h_ms','total_ms'])
with (ROOT/'experiments/datasets.csv').open() as f:
    for case in csv.DictReader(f):
        for block in [64, 128, 256, 512]:
            for repeat in range(10):
                result = subprocess.run([str(ROOT/'materials/build/gpu'), case['n'], str(block), case['seed']],
                                        check=True, capture_output=True, text=True, timeout=120)
                sys.stderr.write(result.stderr)
                row = next(csv.reader(io.StringIO(result.stdout.splitlines()[1])))
                writer.writerow([case['size'], repeat, *row])
