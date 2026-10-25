#!/usr/bin/env python3
"""SPDX-License-Identifier: MIT
Capture quatro cenários em processos separados; não sobrescreva evidências.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='diretório novo para as evidências')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    output = args.output.resolve()
    compiler = shlex.split(os.environ.get('CC', 'cc'))
    binary = str(output / 'lifetimes')
    command = compiler + ['-std=c11', '-Wall', '-Wextra', '-Wpedantic', '-O0', '-g',
                          '-fsanitize=address', '-fno-omit-frame-pointer',
                          str(Path(__file__).with_name('lifetimes.c')), '-o', binary]
    build = subprocess.run(command, capture_output=True, text=True, timeout=30)
    (output / 'build.stdout').write_text(build.stdout)
    (output / 'build.stderr').write_text(build.stderr)
    data = {'platform': platform.platform(), 'compile': command,
            'compiler': subprocess.check_output(compiler + ['--version'], text=True, timeout=5),
            'cases': {}}
    if build.returncode:
        print(build.stderr, file=sys.stderr)
        return 2
    env = dict(os.environ)
    env['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1:exitcode=99'
    env['LSAN_OPTIONS'] = 'exitcode=98'
    data['sanitizer'] = {key: env[key] for key in ('ASAN_OPTIONS', 'LSAN_OPTIONS')}
    failures = 0
    for name in ('borrowed', 'owner-null', 'copy', 'reset'):
        run = subprocess.run([binary, name], capture_output=True, timeout=10, env=env)
        (output / (name + '.stdout')).write_bytes(run.stdout)
        (output / (name + '.stderr')).write_bytes(run.stderr)
        if name == 'owner-null':
            valid = (run.returncode != 0 and all(marker in run.stderr for marker in
                     (b'heap-use-after-free', b'freed by', b'previously allocated')))
        else:
            expected = (b'Club\n' if name != 'reset' else
                        b'old_generation=1 current_generation=2\nold_handle_valid=0 addressable=Rust\n')
            valid = run.returncode == 0 and run.stdout == expected and not run.stderr
        data['cases'][name] = {'command': [binary, name], 'status': run.returncode,
                               'expected_observation': valid}
        failures += not valid
        print(f'{name}: status={run.returncode}; coleta {"OK" if valid else "FALHOU"}')
    (output / 'results.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f'4 cenários; {failures} falhas de preparação. O relato ainda deve explicar as evidências.')
    return int(bool(failures))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, subprocess.SubprocessError) as error:
        print(f'Coleta incompleta: {error}', file=sys.stderr)
        sys.exit(2)
