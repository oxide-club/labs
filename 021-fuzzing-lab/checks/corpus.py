# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import sys
source=Path(__file__).resolve().parents[1]/'materials/corpus.json'
destination=Path(sys.argv[1]); destination.mkdir(parents=True,exist_ok=True)
for name, seed in json.loads(source.read_text()).items():
    (destination/name).write_bytes(bytes.fromhex(seed['hex']))
print('corpus: 4 seeds')
