"""SPDX-License-Identifier: MIT — Alpine/Clang descartável, sem execução no host."""
import argparse
import concurrent.futures
from contextlib import contextmanager
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def digest_file(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def verify_file(path, digest):
    if path.is_symlink() or not path.is_file() or digest_file(path) != digest:
        raise ValueError('SHA256 divergente ou arquivo inválido: ' + str(path))


def safe_path(root, name):
    if Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('Caminho externo recusado')
    result = root / name
    for path in [result, *result.parents]:
        if path == root.parent:
            break
        if path.is_symlink():
            raise ValueError('Link simbólico recusado: ' + str(path))
    return result


def qemu_command(state, inputs, outputs):
    def escaped(path):
        return str(path).replace(',', ',,')
    # Diskless root lives in RAM; the small virtual FAT carries only boot settings.
    return ['qemu-system-x86_64', '-machine', 'q35,accel=' + ('kvm:tcg' if os.access('/dev/kvm',os.R_OK | os.W_OK) else 'tcg'), '-m', '2048', '-smp', '2',
            '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot',
            '-kernel', str(state / 'vmlinuz-virt'), '-initrd', str(state / 'initramfs-virt'),
            '-append', 'console=ttyS0 modules=loop,squashfs,sd-mod,usb-storage quiet apkovl=/dev/vda1:vfat:oxide.apkovl.tar.gz',
            '-cdrom', str(state / 'base.iso'),
            '-drive', 'file=fat:ro:' + escaped(inputs / 'seed') + ',format=raw,if=virtio,readonly=on',
            '-nic', 'none',
            '-virtfs', 'local,path=' + escaped(inputs) + ',mount_tag=inputs,security_model=none,readonly=on',
            '-virtfs', 'local,path=' + escaped(outputs) + ',mount_tag=outputs,security_model=none']


def copy_package(source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    extensions = {'.md','.txt','.c','.h','.py','.json','.csv','.rs','.S','.s','.cu','.toml','.go'}
    top = {'Makefile','README.md','index.md','references.md','report-template.md','LICENSING.md','SOURCE.txt'}
    for path in source.rglob('*'):
        rel = path.relative_to(source)
        if any(part in {'build','target','dist','results','__pycache__','solutions','node_modules'}
               or part.startswith('.') for part in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError('Link simbólico no pacote: ' + str(rel))
        if not path.is_file():
            continue
        if len(rel.parts) == 1:
            include = path.name in top
        else:
            include = rel.parts[0] in {'materials','checks','experiments','licenses'} and (
                path.name in {'Makefile','go.mod'} or path.suffix in extensions)
        if include:
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def guest_session():
    return '''#!/bin/sh
unset OXIDE_DISPOSABLE_VM
printf '\\nVM descartável Oxide: sem rede; somente pacote e pasta de resultados compartilhados.\\n'
printf 'Confirme no console do QEMU. Digite confirmed para executar: '
read -r confirmation
if [ "$confirmation" != confirmed ]; then
    echo 'Recusa: confirmação explícita dentro da VM necessária.' >&2
    exit 2
fi
export OXIDE_DISPOSABLE_VM=confirmed
cd /home/lab/work || exit 1
if [ -f /mnt/inputs/interactive ]; then
    exec sh /mnt/inputs/action.sh
fi
sh /mnt/inputs/action.sh > results/command-stdout.txt 2> results/command-stderr.txt
status=$?
cat results/command-stdout.txt
cat results/command-stderr.txt >&2
exit "$status"
'''


def root_session():
    return '''#!/bin/sh
set -eu
mkdir -p /mnt/inputs /mnt/outputs
mount -t 9p -o trans=virtio,version=9p2000.L,ro inputs /mnt/inputs
mount -t 9p -o trans=virtio,version=9p2000.L outputs /mnt/outputs
finish() {
    status=$?
    printf '%s\\n' "$status" > /mnt/outputs/exit-status
    sync
    poweroff -f
}
trap finish EXIT
printf 'Instalando toolchain fixada, sem rede...\\n'
apk add --no-network --force-non-repository /mnt/inputs/packages/*.apk > /mnt/outputs/install.log 2>&1 || {
    cat /mnt/outputs/install.log
    exit 1
}
adduser -D lab
mkdir -p /home/lab/work
cp -a /mnt/inputs/lab/. /home/lab/work/
chown -R lab:lab /home/lab/work
mkdir -p /home/lab/work/results
mount --bind /mnt/outputs /home/lab/work/results
printf 'oxide-disposable-qemu\\n' > /etc/oxide-lab-guest
chmod 444 /etc/oxide-lab-guest
apk info -v > /mnt/outputs/packages.txt
uname -a > /mnt/outputs/kernel.txt
clang --version > /mnt/outputs/compiler.txt
export CC=clang
su -s /bin/sh lab -c /usr/local/bin/oxide-session
'''


def seed_files(directory):
    files = {
        'etc/.default_boot_services': '',
        'etc/apk/world': 'alpine-base\n',
        'etc/inittab': '''::sysinit:/sbin/openrc sysinit
::sysinit:/sbin/openrc boot
::wait:/sbin/openrc default
ttyS0::once:/usr/local/bin/oxide-root-session
::shutdown:/sbin/openrc shutdown
''',
        'usr/local/bin/oxide-root-session': root_session(),
        'usr/local/bin/oxide-session': guest_session(),
    }
    directory.mkdir(parents=True, exist_ok=True)
    with tarfile.open(directory / 'oxide.apkovl.tar.gz', 'w:gz') as archive:
        for name, content in files.items():
            data = content.encode()
            member = tarfile.TarInfo(name)
            member.size = len(data)
            member.uid = member.gid = 0
            member.mode = 0o755 if name.startswith('usr/') else 0o644
            archive.addfile(member, io.BytesIO(data))


def asset_records(config):
    records = [config['image'], *config['packages']]
    names = set()
    for record in records:
        name = record['file']
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+-]*', name) or name in names:
            raise ValueError('Nome de insumo inválido: ' + name)
        names.add(name)
    return records


def recipe_digest(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode() + Path(__file__).read_bytes()).hexdigest()


def write_ready(config, state):
    assets = {record['file']: record['sha256'] for record in asset_records(config)}
    assets.update({name:digest_file(safe_path(state,name)) for name in ('vmlinuz-virt','initramfs-virt')})
    ready = {'recipe':recipe_digest(config), 'assets':assets}
    safe_path(state,'ready.json').write_text(json.dumps(ready,indent=2)+'\n')


def check_ready(config, state):
    ready = safe_path(state,'ready.json')
    if not ready.is_file():
        raise ValueError('VM não preparada; execute make env-setup')
    record = json.loads(ready.read_text())
    if record.get('recipe') != recipe_digest(config):
        raise ValueError('Receita mudou; execute make env-setup')
    expected = {r['file']:r['sha256'] for r in asset_records(config)}
    if not all(record['assets'].get(name) == digest for name,digest in expected.items()):
        raise ValueError('Manifesto de preparação divergente; execute make env-setup')
    if set(record['assets']) != set(expected) | {'vmlinuz-virt','initramfs-virt'}:
        raise ValueError('Manifesto de preparação incompleto; execute make env-setup')
    for name, digest in record['assets'].items():
        verify_file(safe_path(state,name),digest)


def download(record, state, cache=None):
    target = safe_path(state,record['file'])
    if target.exists():
        verify_file(target,record['sha256'])
        return
    if cache:
        source = safe_path(cache,record['file'])
        if source.exists():
            verify_file(source,record['sha256'])
            shutil.copyfile(source,target)
            return
    temporary = safe_path(state,record['file']+'.download')
    print('Baixando ' + record['file'], flush=True)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(record['url'],timeout=60) as response, temporary.open('wb') as output:
                shutil.copyfileobj(response,output)
            verify_file(temporary,record['sha256'])
            temporary.replace(target)
            return
        except OSError:
            if attempt == 2:
                raise
            time.sleep(1)
        finally:
            temporary.unlink(missing_ok=True)


def prepare(config, state):
    for tool in ('qemu-system-x86_64','bsdtar'):
        if not shutil.which(tool):
            raise ValueError('Dependência ausente: ' + tool)
    cache = Path(os.environ['ENV_ASSETS']).resolve() if os.environ.get('ENV_ASSETS') else None
    if os.environ.get('ENV_ISO'):
        source = Path(os.environ['ENV_ISO']).resolve()
        verify_file(source,config['image']['sha256'])
        target = safe_path(state,config['image']['file'])
        if source != target.resolve():
            shutil.copyfile(source,target)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda record:download(record,state,cache),asset_records(config)))
    for name in ('vmlinuz-virt','initramfs-virt'):
        target = safe_path(state,name)
        with target.open('wb') as stream:
            subprocess.run(['bsdtar','-xOf',str(state / config['image']['file']),'boot/'+name],
                           stdout=stream,check=True,timeout=60)
    write_ready(config,state)
    print('Imagem e pacotes verificados. VM Alpine/Clang pronta para execução sem rede.')


def clean_state(config, state):
    names = [r['file'] for r in asset_records(config)] + ['vmlinuz-virt','initramfs-virt','ready.json']
    names += [r['file']+'.download' for r in asset_records(config)]
    paths = [safe_path(state,name) for name in names]
    for path in paths:
        if path.exists() and not path.is_file():
            raise ValueError('Arquivo de ambiente inválido: '+str(path))
    for path in paths:
        path.unlink(missing_ok=True)
    print('Insumos locais removidos; resultados e arquivos próprios preservados.')


def execute(config, state, action):
    check_ready(config,state)
    if not sys.stdin.isatty():
        raise ValueError('Use um terminal interativo para confirmar dentro da VM; make env-shell')
    result_root = safe_path(ROOT,'results'); result_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='session-',dir=state) as directory:
        inputs = Path(directory) / 'inputs'; inputs.mkdir()
        copy_package(ROOT,inputs / 'lab')
        packages = inputs / 'packages'; packages.mkdir()
        for record in config['packages']:
            os.link(safe_path(state,record['file']),packages / record['file'])
        if action == 'shell':
            action_script = 'exec /bin/sh\n'
            (inputs / 'interactive').touch()
        else:
            argv = ['make',action,'CC=clang']
            for name,default in [('VARIANT','reference'),('MODE','gpu'),('EXPERIMENT','default')]:
                argv.append(name+'='+os.environ.get(name,default))
            action_script = 'exec ' + shlex.join(argv) + '\n'
        (inputs / 'action.sh').write_text(action_script)
        seed_files(inputs / 'seed')
        outputs = Path(tempfile.mkdtemp(prefix='vm-',dir=result_root))
        # Guest UID 1000 can only write this freshly-created output directory.
        outputs.chmod(0o777)
        (outputs / 'environment.json').write_text(json.dumps(config,indent=2)+'\n')
        print('QEMU sem rede. Confirme no console do guest. Evidências: '+str(outputs),flush=True)
        subprocess.run(qemu_command(state,inputs,outputs),check=True,timeout=3600)
        status = outputs / 'exit-status'
        if status.is_symlink() or not status.is_file():
            raise ValueError('Sessão interrompida; resultado não confirmado')
        value = status.read_text().strip()
        if value not in {str(n) for n in range(256)}:
            raise ValueError('Status inválido no guest')
        return int(value)


@contextmanager
def locked_state(state):
    state.mkdir(exist_ok=True)
    with safe_path(state,'.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Outro comando de ambiente está em execução') from None
        yield


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['setup','shell','clean','exec'])
    parser.add_argument('command',nargs='?',choices=['test','run','verify-preparation'])
    args = parser.parse_args()
    if args.action == 'exec' and not args.command:
        parser.error('exec exige um comando')
    config = json.loads((ROOT / 'materials/environment.json').read_text())
    state = safe_path(ROOT,'.lab-env')
    with locked_state(state):
        if args.action == 'setup':
            prepare(config,state)
            return 0
        if args.action == 'clean':
            clean_state(config,state)
            return 0
        return execute(config,state,'shell' if args.action == 'shell' else args.command)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError,ValueError,subprocess.SubprocessError) as error:
        print('ERRO: '+str(error),file=sys.stderr)
        raise SystemExit(1)
