"""SPDX-License-Identifier: MIT — gere relatos locais a partir do template canônico."""
from pathlib import Path
import argparse
import re
import sys
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
content='<!-- Gerado de templates/report-template.md; não edite manualmente. -->\n'+(root/'templates/report-template.md').read_text()
failed=False
for lab in sorted(root.iterdir()):
    if lab.is_dir() and re.fullmatch(r'\d{3}-[a-z0-9-]+',lab.name):
        target=lab/'report-template.md'
        if args.check:
            if not target.exists() or target.read_text()!=content:
                print(f'Relato desatualizado: {lab.name}',file=sys.stderr); failed=True
        else:
            target.write_text(content)
sys.exit(failed)
