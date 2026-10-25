# SPDX-License-Identifier: MIT
"""Build and collect raw evidence; does not decide mitigation conclusions."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    'A': ['-fno-pie', '-fno-stack-protector', '-no-pie', '-Wl,-z,norelro,-z,lazy'],
    'B': ['-fPIE', '-fno-stack-protector', '-pie', '-Wl,-z,norelro,-z,lazy'],
    'C': ['-fno-pie', '-fstack-protector-all', '-no-pie', '-Wl,-z,norelro,-z,lazy'],
    'D': ['-fno-pie', '-fno-stack-protector', '-no-pie', '-Wl,-z,relro,-z,lazy'],
    'E': ['-fno-pie', '-fno-stack-protector', '-no-pie', '-Wl,-z,relro,-z,now'],
    'F': ['-fPIE', '-fstack-protector-all', '-pie', '-Wl,-z,relro,-z,now'],
}

def run(cmd):
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError(f'{shlex.join(map(str, cmd))}: status {result.returncode}\n{result.stderr}')
    return result.stdout

def parse_maps(raw, binary):
    head, maps = raw.split('MAPS\n', 1)
    anchors = {p[1]: int(p[2], 16) for line in head.splitlines()
               if (p := line.split()) and p[0] == 'ANCHOR'}
    if set(anchors) != {'executable', 'stack', 'library', 'anonymous'}:
        raise ValueError('quatro anchors obrigatórios')
    rows = []
    for line in maps.splitlines():
        p = line.split(maxsplit=5)
        start, end = (int(v, 16) for v in p[0].split('-'))
        rows.append((start, end, p[1], int(p[2], 16), p[5] if len(p) > 5 else '', line))
    selected = {}
    for name, address in anchors.items():
        matches = [r for r in rows if r[0] <= address < r[1]]
        if len(matches) != 1:
            raise ValueError(f'anchor sem mapa único: {name}')
        r = matches[0]
        if name == 'executable' and r[4] != str(binary.resolve()):
            raise ValueError('identidade do executável')
        if name == 'stack' and r[4] != '[stack]':
            raise ValueError('identidade da stack')
        if name == 'library' and Path(r[4]).name != 'libc.so.6':
            raise ValueError('identidade da libc')
        if name == 'anonymous' and (r[4] or r[2] != 'rw-p'):
            raise ValueError('identidade da região anônima própria')
        selected[name] = {'anchor': hex(address), 'start': hex(r[0]), 'end': hex(r[1]),
                          'permissions': r[2], 'path': r[4], 'map': r[5]}
    executable_path = selected['executable']['path']
    selected['executable']['base'] = hex(min(r[0] for r in rows if r[4] == executable_path))
    selected['library']['base'] = hex(min(r[0] for r in rows if r[4] == selected['library']['path']))
    return selected

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['build', 'collect'])
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.action == 'build':
        commands = []
        for name, flags in PROFILES.items():
            cmd = ['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O1', '-g', '-fno-lto',
                   *flags, '-Wl,-z,noexecstack', str(ROOT/'materials/c/probe.c'), '-ldl', '-o', str(out/name)]
            commands.append(shlex.join(cmd))
            run(cmd)
        (out/'commands.txt').write_text('\n'.join(commands)+'\n')
        return
    versions = {tool: run([tool, '--version']) for tool in ['gcc', 'ld', 'readelf', 'objdump', 'ldd']}
    versions.update(system=platform.platform(), python=platform.python_version(),
                    loader_environment={k: v for k, v in os.environ.items() if k.startswith(('LD_', 'GLIBC_'))})
    try:
        versions['randomize_va_space'] = Path('/proc/sys/kernel/randomize_va_space').read_text().strip()
    except OSError as e:
        versions['randomize_va_space'] = f'indisponível: {e}'
    (out/'environment.json').write_text(json.dumps(versions, indent=2)+'\n')
    samples = []
    hashes = {}
    for name in PROFILES:
        binary = out/name
        hashes[name] = hashlib.sha256(binary.read_bytes()).hexdigest()
        for suffix, command in [('elf', ['readelf', '-W', '-h', '-l', '-d', '-S', '-s', str(binary)]),
                                ('asm', ['objdump', '-d', '--disassemble=reference_sum', str(binary)])]:
            (out/f'{name}.{suffix}.txt').write_text(run(command))
        raw = run([str(binary), '--maps'])
        parse_maps(raw, binary)
        (out/f'{name}.maps.txt').write_text(raw)
    for name in ['A', 'B']:
        for i in range(20):
            # Each subprocess launches the executable anew, never a fork-only sample.
            raw = run([str(out/name), '--maps'])
            (out/f'{name}-{i:02}.maps.txt').write_text(raw)
            samples.append({'profile': name, 'launch': i, 'regions': parse_maps(raw, out/name)})
    (out/'samples.json').write_text(json.dumps(samples, indent=2)+'\n')
    with (out/'samples.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['profile', 'launch', 'executable_base', 'stack_start', 'library_base', 'anonymous_start'])
        for sample in samples:
            regions = sample['regions']
            writer.writerow([sample['profile'], sample['launch'], regions['executable']['base'],
                             regions['stack']['start'], regions['library']['base'], regions['anonymous']['start']])
    (out/'sha256.json').write_text(json.dumps(hashes, indent=2)+'\n')
    print('coleta completa: seis inspeções, quarenta lançamentos novos; interpretação pendente')

if __name__ == '__main__':
    main()
