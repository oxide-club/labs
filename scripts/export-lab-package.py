# SPDX-License-Identifier: MIT
"""Copie somente formatos distribuídos; não publique nem altere o website."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

spec=importlib.util.spec_from_file_location('validation',Path(__file__).with_name('validate.py'))
validation=importlib.util.module_from_spec(spec);spec.loader.exec_module(validation)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('lab',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
if not validation.ID.fullmatch(a.lab.name):p.error('ID inválido')
a.out.mkdir(parents=True,exist_ok=False)
manifest={}
for file in sorted(a.lab.rglob('*')):
    if file.is_symlink():raise ValueError(f'link simbólico: {file}')
    relative=file.relative_to(a.lab)
    if file.is_file() and validation.distributed(relative):
        target=a.out/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(file,target);manifest[str(relative)]=hashlib.sha256(file.read_bytes()).hexdigest()
# Licenças são adicionadas ao pacote pelo empacotador; mantenha cópia autossuficiente.
shutil.copytree(a.lab.parent/'licenses',a.out/'licenses')
shutil.copyfile(a.lab.parent/'LICENSING.md',a.out/'LICENSING.md')
(a.out/'PACKAGE-REVISION.json').write_text(json.dumps({'preparation':'2026-10-25.1','files':manifest},indent=2)+'\n')
print(f'OK pacote: {a.lab.name}, {len(manifest)} arquivos de conteúdo; licenças e revisão incluídas')
