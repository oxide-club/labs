"""SPDX-License-Identifier: MIT
Verificação local de estrutura; o schema YAML completo pertence ao website.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r'\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*')
SECTIONS = ['O que vamos investigar', 'Antes de começar', 'Materiais',
            'Etapas da investigação', 'Critérios de conclusão', 'Extensões opcionais',
            'Participação no clube', 'Referências e atividades relacionadas']
REQUIRED = ['title', 'slug', 'summary', 'question', 'draft', 'topics',
            'prerequisites', 'tools', 'environment', 'difficulty', 'area']


def prose(text):
    """Ignore exemplos cercados por fences ao verificar títulos e links."""
    result = []
    fence = None
    for line in text.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            token = match[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            result.append(line)
    return '\n'.join(result)


def distributed(path):
    parts = path.parts
    if any(not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]*', part) for part in parts):
        return False
    if len(parts) == 1:
        return parts[0] in ['index.md','README.md','references.md','report-template.md']
    return (parts[0] in ['materials','checks','experiments']
            and not set(parts[1:-1]) & {'node_modules','__pycache__','target','build','dist','solutions'}
            and (path.name in {'Makefile', 'go.mod'} or path.suffix in {'.md','.txt','.c','.h','.py','.json','.csv','.rs','.S','.s','.cu','.toml','.go'}))


def load_areas(root):
    path = root/'areas.json'
    if path.is_symlink() or not path.is_file():
        raise ValueError('areas.json deve ser um arquivo regular')
    areas = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(areas, list) or not areas:
        raise ValueError('areas.json deve conter áreas')
    for area in areas:
        if not isinstance(area, dict) or any(
            not isinstance(area.get(key), str) or not area[key].strip()
            for key in ['id', 'slug', 'title', 'description']
        ) or any(not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', area[key]) for key in ['id', 'slug']):
            raise ValueError('área inválida em areas.json')
    for key in ['id', 'slug']:
        if len({a[key] for a in areas}) != len(areas):
            raise ValueError(f'{key} duplicado em areas.json')
    return areas


def validate_lab(lab):
    errors = []
    if not ID.fullmatch(lab.name):
        errors.append('ID inválido')
    if lab.is_symlink():
        return ['diretório simbólico não permitido']
    files = list(lab.rglob('*'))
    for file in files:
        if file.is_symlink():
            errors.append(f'link simbólico: {file.relative_to(lab)}')
    for name in ['index.md', 'README.md', 'references.md', 'report-template.md', 'materials/README.md']:
        if not (lab/name).is_file():
            errors.append(f'arquivo necessário ausente: {name}')
    index = lab/'index.md'
    if not index.is_file():
        return errors
    text = index.read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
    if not match:
        errors.append('front matter ausente')
        body = text
    else:
        metadata = dict(re.findall(r'^(\w+):\s*(.*)$', match[1], re.M))
        for key in REQUIRED:
            if not metadata.get(key, '').strip():
                errors.append(f'metadado necessário: {key}')
        if not metadata.get('title', '').strip('\'"').startswith('Laboratório de '):
            errors.append('title deve começar com Laboratório de ')
        if metadata.get('slug', '').strip('\'"') != lab.name:
            errors.append('slug difere do diretório')
        if metadata.get('draft') not in ['true', 'false']:
            errors.append('draft deve ser booleano')
        if metadata.get('draft') == 'false' and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', metadata.get('publishedAt','')):
            errors.append('publicação sem publishedAt')
        if metadata.get('difficulty') not in ['beginner','intermediate','advanced']:
            errors.append('difficulty inválida')
        try:
            areas = load_areas(lab.parent)
            area = metadata.get('area', '').strip().strip('\"\'')
            if area not in {entry['id'] for entry in areas}:
                errors.append('area deve referenciar um ID de areas.json')
        except (ValueError, OSError) as error:
            errors.append(str(error))
        body = text[match.end():]
    headings = re.findall(r'^## (.+)$', prose(body), re.M)
    if headings != SECTIONS:
        errors.append('oito seções H2 ausentes ou fora de ordem')
    for file in files:
        if file.is_symlink() or not file.is_file() or file.suffix != '.md':
            continue
        content = prose(file.read_text(encoding='utf-8'))
        links = re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', content)
        links += re.findall(r'^\s*\[[^\]]+\]:\s*(\S+)', content, re.M)
        for url in links:
            url = url.strip('<>')
            parsed = urlsplit(url)
            if parsed.scheme in ['http','https','mailto'] or url.startswith(('/', '#')):
                continue
            if parsed.scheme:
                errors.append(f'{file.relative_to(lab)}: protocolo não permitido {url}')
                continue
            target = (file.parent/unquote(parsed.path)).resolve()
            if (not target.is_relative_to(lab.resolve()) or not target.is_file()
                    or not distributed(target.relative_to(lab.resolve()))):
                errors.append(f'{file.relative_to(lab)}: link local ausente ou externo ao pacote: {url}')
    return errors


def fixture_manifest(root):
    """Dados distribuídos; código, documentação e artefatos não são fixtures."""
    manifest = {}
    for lab in sorted(root.iterdir()):
        if lab.is_dir() and not lab.is_symlink() and ID.fullmatch(lab.name):
            for file in sorted(lab.rglob('*')):
                if (file.is_file() and not file.is_symlink() and distributed(file.relative_to(lab))
                        and file.suffix in ['.txt','.json','.csv']):
                    manifest[file.relative_to(root).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return manifest


def check_manifest(root, expected):
    actual = fixture_manifest(root)
    return [f'fixture ausente, novo ou alterado: {name}' for name in sorted(actual.keys() | expected.keys())
            if actual.get(name) != expected.get(name)]


def validate_catalog(root, catalog):
    errors=[]; identifiers=set(); numbers=set()
    for entry in catalog:
        identifier=entry.get('id','')
        if not ID.fullmatch(identifier):
            errors.append(f'ID inválido no catálogo: {identifier}'); continue
        if identifier in identifiers or identifier[:3] in numbers:
            errors.append(f'ID ou número duplicado: {identifier}')
        identifiers.add(identifier); numbers.add(identifier[:3])
    for lab in sorted(root.iterdir()):
        if lab.is_dir() and ID.fullmatch(lab.name) and lab.name not in identifiers:
            errors.append(f'diretório não registrado: {lab.name}')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--update-fixtures', action='store_true', help='registre hashes somente após conferir os dados')
    args=parser.parse_args()
    root=args.root.resolve(); errors=[]
    labs=[p for p in sorted(root.iterdir()) if p.is_dir() and ID.fullmatch(p.name)]
    catalog=root/'docs/catalogo.json'
    if catalog.exists():
        errors += validate_catalog(root,json.loads(catalog.read_text()))
    for lab in labs:
        errors += [f'{lab.name}: {error}' for error in validate_lab(lab)]
    for path in ['LICENSING.md','licenses/MIT.txt','licenses/CC-BY-4.0.txt','licenses/CC0-1.0.txt']:
        if not (root/path).is_file(): errors.append(f'licença ausente: {path}')
    manifest=root/'docs/fixtures-sha256.json'
    if args.update_fixtures:
        manifest.write_text(json.dumps(fixture_manifest(root),indent=2,ensure_ascii=False)+'\n')
    elif manifest.exists():
        errors += check_manifest(root,json.loads(manifest.read_text()))
    else:
        errors.append('manifest de fixtures ausente')
    for error in errors: print('ERRO:',error,file=sys.stderr)
    print(f'{len(labs)} laboratórios inspecionados; {len(errors)} erros estruturais.')
    return bool(errors)

if __name__=='__main__': sys.exit(main())
