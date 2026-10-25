"""SPDX-License-Identifier: MIT — verificação seletiva da preparação de variantes.

Não aprova soluções: cada rejeição esperada exige status e diagnóstico conhecidos.
CUDA aqui significa somente compilação, nunca aprovação de runtime.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preparation', ROOT/'scripts/verify-preparation.py')
preparation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparation)


def main():
    config = json.loads((ROOT/'docs/variant-checks.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', action='append', choices=sorted(config), required=True)
    parser.add_argument('--root', type=Path, default=ROOT, help='raiz dos pacotes extraídos')
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix='oxide-variants-') as directory:
        for name in args.variant:
            variant = config[name]
            work = Path(directory)/name
            work.mkdir(exist_ok=True)
            for check in variant['checks']:
                result = preparation.run_check(args.root.resolve()/variant['lab'], work, check)
                result.update(variant=name, lab=variant['lab'])
                results.append(result)
                print(('OK' if result['ok'] else 'FALHOU')+': '+name+': '+check['name'])
                if not result['ok']:
                    print(result.get('reason', '')+result.get('stdout', '')+result.get('stderr', ''))
                    break
            if name == 'gpu-cuda':
                print('NÃO EXECUTADO: kernels GPU e benchmarks; este seletor verifica somente build.')
    if args.json:
        args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
    return int(any(not result['ok'] for result in results))


if __name__ == '__main__':
    raise SystemExit(main())
