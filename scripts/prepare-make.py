"""SPDX-License-Identifier: MIT — gere pacotes Make independentes."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
MAKE = '''# SPDX-License-Identifier: MIT
# Gerado por scripts/prepare-make.py; dados em docs/make-labs.json.
.DEFAULT_GOAL := help
PYTHON ?= python3
export VARIANT ?= reference
export MODE ?= gpu
export EXPERIMENT ?= default
export CC
.PHONY: help setup build test run clean verify-preparation
help setup build test run clean verify-preparation:
\t@$(PYTHON) materials/lab.py $@
'''


def generated():
    labs = json.loads((ROOT / 'docs/make-labs.json').read_text())
    preparation = json.loads((ROOT / 'docs/preparation-checks.json').read_text())
    variants = json.loads((ROOT / 'docs/variant-checks.json').read_text())
    for name, manifest in labs.items():
        for variant in manifest['variants'].values():
            for config in variant.get('modes', {'default': variant}).values():
                selector = config.pop('preparation_variant', None)
                config['preparation'] = variants[selector]['checks'] if selector else preparation[name]
        files = {'Makefile': MAKE, 'materials/lab.json': json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                 'materials/lab.py': (ROOT / 'templates/make/lab.py').read_text(),
                 'materials/preparation.py': (ROOT / 'scripts/verify-preparation.py').read_text()}
        if manifest.get('isolated'):
            files['Makefile'] += '''.PHONY: env-setup env-shell env-clean
env-setup env-shell env-clean:
\t@$(PYTHON) materials/environment.py $(patsubst env-%,%,$@)
'''
            for filename in ('environment.py', 'environment.json', 'environment.md'):
                source = ROOT / 'templates/make' / filename
                if source.exists():
                    files['materials/' + filename] = source.read_text()
        for relative, content in files.items():
            yield ROOT / name / relative, content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for path, content in generated():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text(content)
    for name in stale:
        print('Desatualizado: ' + name, file=sys.stderr)
    return bool(stale)

if __name__ == '__main__':
    sys.exit(main())
