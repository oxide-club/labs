"""SPDX-License-Identifier: MIT — interface independente do laboratório."""
import argparse
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def local_path(name):
    path = ROOT / name
    if Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('Caminho fora do laboratório: ' + name)
    for part in [path, *path.parents]:
        if part == ROOT.parent:
            break
        if part.is_symlink():
            raise ValueError('Link simbólico recusado: ' + str(part))
    return path


def command(argv, *, timeout=180, stdin=None, env=None, log=None):
    print('+ ' + shlex.join(argv), flush=True)
    with open(stdin, 'rb') if stdin else open(os.devnull, 'rb') as source:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdin=source, start_new_session=True,
                                   stdout=subprocess.PIPE if log else None,
                                   stderr=subprocess.PIPE if log else None)
        try:
            if log:
                out, err = process.communicate(timeout=timeout)
                code = process.returncode
                Path(str(log) + '-stdout.txt').write_bytes(out)
                Path(str(log) + '-stderr.txt').write_bytes(err)
                Path(str(log) + '-status.txt').write_text(str(code) + '\n')
                sys.stdout.buffer.write(out)
                sys.stderr.buffer.write(err)
            else:
                code = process.wait(timeout=timeout)
        except BaseException as error:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if log:
                out, err = process.communicate()
                Path(str(log) + "-stdout.txt").write_bytes(out)
                Path(str(log) + "-stderr.txt").write_bytes(err)
                reason = "timeout" if isinstance(error, subprocess.TimeoutExpired) else "interrupted"
                Path(str(log) + "-status.txt").write_text(reason + "\n")
            else:
                process.wait()
            raise
    if code:
        raise subprocess.CalledProcessError(code, argv)


def expand(argv, work, result):
    replacements = {'{work}': str(work), '{result}': str(result), '{lab}': str(ROOT)}
    values = []
    for arg in argv:
        for old, new in replacements.items():
            arg = arg.replace(old, new)
        values.append(arg)
    if values[0] == 'cc':
        values[0] = os.environ.get('CC', 'cc')
    if values[0] == 'python3':
        values[0] = sys.executable
    if values[0] == 'make':
        values[0] = os.environ.get('MAKE', 'make')
        # Keep nested builds local even if BUILD is exported by the caller.
        values.append('BUILD=build' if work == ROOT / 'build' else 'BUILD=' + str(work))
        values.append('CC=' + os.environ.get('CC', 'cc'))
    return values


def setup(config):
    if sys.version_info < (3, 10):
        raise ValueError('Python 3.10+ necessário')
    if platform.system() != 'Linux':
        raise ValueError('Este roteiro exige Linux')
    if config.get('x86_64') and platform.machine() != 'x86_64':
        raise ValueError('Este roteiro exige Linux x86-64')
    for tool in config['tools']:
        tool = os.environ.get('CC', 'cc') if tool == 'cc' else tool
        if not shutil.which(tool):
            raise ValueError('Dependência ausente: ' + tool)
    print('Ferramentas disponíveis: ' + ', '.join(config['tools']))
    print('Disponibilidade não comprova runtime, sanitizers ou conclusão do exercício.')


def steps(entries, work, result, record=False):
    for index, entry in enumerate(entries):
        if isinstance(entry, list):
            entry = {'argv': entry}
        argv = expand(entry['argv'], work, result)
        command(argv, timeout=entry.get('timeout', 180),
                stdin=local_path(entry['stdin']) if 'stdin' in entry else None,
                log=result / f'{index:02}' if record else None)


def clean(config):
    paths = [local_path(name) for name in config.get('artifacts', [])]
    # Validate every path before deleting any file. Never remove whole trees.
    for path in paths:
        if path.exists() and not path.is_file():
            raise ValueError('Artefato não é arquivo regular: ' + str(path))
    for path in paths:
        path.unlink(missing_ok=True)
    for parent in sorted({p.parent for p in paths}, key=lambda p: len(p.parts), reverse=True):
        while parent != ROOT and parent.name not in ('materials', 'checks', 'experiments'):
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    print('Artefatos conhecidos removidos; relatos e results/ preservados.')


def guest_confirmed():
    marker = Path('/etc/oxide-lab-guest')
    return (marker.is_file() and marker.stat().st_uid == 0
            and marker.read_text().strip() == 'oxide-disposable-qemu'
            and os.geteuid() != 0
            and os.environ.get('OXIDE_DISPOSABLE_VM') == 'confirmed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('help','setup','build','test','run','clean','verify-preparation'))
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'materials/lab.json').read_text())
    variant, mode = os.environ.get('VARIANT', 'reference'), os.environ.get('MODE', 'gpu')
    if variant not in manifest['variants']:
        raise ValueError('VARIANT desconhecida: ' + variant)
    config = manifest['variants'][variant]
    if 'modes' in config:
        if mode not in config['modes']:
            raise ValueError('MODE desconhecido: ' + mode)
        config = config['modes'][mode]
    action = args.action
    if action == 'help':
        print(manifest['name'])
        print('make setup | build | test | run | clean | verify-preparation')
        print('VARIANT=' + '|'.join(manifest['variants']))
        if 'modes' in manifest['variants'][variant]:
            print('MODE=gpu|cpu (CPU é suporte auxiliar, não valida CUDA)')
        print('EXPERIMENT=' + '|'.join(config.get('experiments', {'default': []})))
        print('Dependências: ' + ', '.join(config['tools']))
        print(config.get('note', 'Starter incompleto: test pode falhar até implementar.'))
        if manifest.get('isolated'):
            print('Execução em VM descartável: make env-setup | env-shell | env-clean')
        return 0
    if action == 'clean':
        # Clean artifacts of every available variant, independent of selection.
        all_configs = []
        for v in manifest['variants'].values():
            all_configs.extend(v.get('modes', {'default': v}).values())
        clean({'artifacts': sorted({p for c in all_configs for p in c.get('artifacts', [])})})
        return 0
    if action in ('run','test','verify-preparation') and manifest.get('isolated') and not guest_confirmed():
        helper = ROOT / 'materials/environment.py'
        if not helper.exists():
            raise ValueError('VM necessária; prepare com make env-setup')
        # Inherit stdin for explicit confirmation at the guest console.
        return subprocess.call([sys.executable, str(helper), 'exec', action], cwd=ROOT)
    setup(config)
    if action == 'setup':
        local_path('materials/build')
        steps(config.get('setup', []), local_path('build'), ROOT / 'results')
        return 0
    work = local_path('build')
    local_path('materials/build')
    result = ROOT / 'results'
    if action == 'verify-preparation':
        from preparation import run_check
        print('Preparação do starter original; após editar, use make test para verificar a solução.')
        with tempfile.TemporaryDirectory(prefix='oxide-preparation-') as temp:
            for check in config['preparation']:
                # run_check expands {work}/{lab}; select compiler consistently.
                check = dict(check)
                check['argv'] = expand(check['argv'], Path(temp), result)
                record = run_check(ROOT, Path(temp), check)
                print(('OK: ' if record['ok'] else 'FALHOU: ') + check['name'])
                if not record['ok']:
                    print(record.get('reason', '') + record.get('stdout', '') + record.get('stderr', ''))
                    return 1
        print(config.get('preparation_note', 'Preparação verificada; não aprova a solução.'))
        return 0
    experiment = os.environ.get('EXPERIMENT', 'default')
    if action == 'run' and experiment not in config.get('experiments', {}):
        raise ValueError('EXPERIMENT desconhecido: ' + experiment)
    work.mkdir(exist_ok=True)
    steps(config.get('build', []), work, result)
    if not config.get('build'):
        print('Sem compilação: fontes interpretados.')
    if action == 'test':
        steps(config['test'], work, result)
    elif action == 'run':
        local_path('results').mkdir(exist_ok=True)
        result = Path(tempfile.mkdtemp(prefix=time.strftime('%Y%m%d-%H%M%S-'), dir=ROOT / 'results'))
        print('Evidências desta execução: ' + str(result))
        try:
            steps(config['experiments'][experiment], work, result, record=True)
        finally:
            for name in config.get('evidence', []):
                source = local_path(name)
                if source.is_file():
                    shutil.copyfile(source, result / source.name)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print('ERRO: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
