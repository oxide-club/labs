#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute no pacote exportado após compilar o runner; não testa conclusão."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
for name in ('instructor.md','correct.c','reserve-a.bin','reserve-b.bin'):
    assert not list(root.rglob(name)), f'Material de outra fase no pacote: {name}'
kit=root/'materials/after-campaign'
assert sorted(root.rglob('regression.py')) == [kit/'regression.py']
manifest=json.loads((kit/'reproducers.json').read_text())
assert manifest['parser_sha256'] == hashlib.sha256((root/'materials/starter/c/oxf.c').read_bytes()).hexdigest()
assert len(manifest['reproducers']) == 2
for item in manifest['reproducers']:
    assert hashlib.sha256(bytes.fromhex(item['hex'])).hexdigest() == item['sha256']
assert (kit/'README.md').is_file()
for options in ([],['--smoke']):
    result=subprocess.run([sys.executable,str(root/'checks/check.py'),str(root/'materials/starter/c/build/runner'),*options],capture_output=True,text=True,timeout=5)
    if result.returncode==2:
        print(result.stdout); raise SystemExit(2)
    assert result.returncode==0, 'Check anterior à campanha não passou.'
    assert 'PREPARATION_OK' in result.stdout
    assert not result.stderr and 'SUMMARY:' not in result.stdout and 'expected=' not in result.stdout
result=subprocess.run(['make','-C',str(root/'materials/starter/c'),'fuzz'],capture_output=True,text=True,timeout=30)
assert result.returncode!=0 and 'Implemente o target' in result.stderr, 'Target inicial deixou de ser incompleto.'
print('PHASE_SEPARATION_OK: preparação aprovada, target incompleto, kit posterior público e íntegro; preparação não revela os defeitos.')
