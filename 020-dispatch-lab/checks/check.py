# SPDX-License-Identifier: MIT
"""Checks de API independentes; 0 aprovado, 1 propriedade, 2 infraestrutura."""
import argparse
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def environment(cargo_home=None, profile='inspect0'):
    env=os.environ.copy()
    for key in list(env):
        if key.startswith('CARGO_') or key in ('RUSTFLAGS','RUSTC','RUSTDOC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTC_BOOTSTRAP'):
            del env[key]
    env['RUSTC_WRAPPER']=''
    env['RUSTC_WORKSPACE_WRAPPER']=''
    if cargo_home is not None:
        env['CARGO_HOME']=str(cargo_home)
    env['CARGO_ENCODED_RUSTFLAGS']='\x1f'.join(['-C',f'opt-level={level(profile)}','-C','lto=off','-C','codegen-units=1','-C','debuginfo=2','-C','panic=unwind'])
    return env

def level(profile):
    return {'inspect0': '0', 'inspect3': '3'}[profile]

def reject_configs(work):
    # Cargo searches cwd ancestors even with an explicit manifest path.
    for directory in [work.resolve(), *work.resolve().parents]:
        for name in ['config', 'config.toml']:
            path=directory/'.cargo'/name
            if path.exists():
                raise ValueError(f'configuração Cargo externa recusada: {path}; use uma pasta sem .cargo/config ancestral')

def cargo_command(action, work, profile, target):
    reject_configs(work)
    cmd=['cargo',action,'--locked','--offline','-vv','--manifest-path',str(work/'Cargo.toml'),
         '--profile',profile,'--target',target,'--target-dir',str(work/'target'/profile)]
    for key,value in [('opt-level',level(profile)),('debug','2'),('lto','false'),('codegen-units','1'),('panic','"unwind"')]:
        cmd += ['--config',f'profile.{profile}.{key}={value}']
    return cmd

def verify_compiler(log, profile):
    commands=[]
    for line in log.splitlines():
        if 'Running `' not in line or '--crate-name ' not in line:
            continue
        command=shlex.split(line.split('Running `',1)[1].rsplit('`',1)[0])
        if not any(Path(token).name=='rustc' for token in command):
            continue
        crate=command[command.index('--crate-name')+1]
        if crate not in ('dispatch_core','dispatch_harness'):
            continue
        flags={}
        for i, token in enumerate(command):
            value=command[i+1] if token=='-C' else token[2:] if token.startswith('-C') else ''
            if '=' in value:
                key,val=value.split('=',1);flags[key]=val
        required={'opt-level':level(profile),'lto':'off','codegen-units':'1','debuginfo':'2','panic':'unwind'}
        if any(flags.get(key)!=value for key,value in required.items()):
            raise ValueError(f'flags rustc divergentes em {crate}: {flags}')
        commands.append({'crate':crate,'argv':command,'effective':{k:flags[k] for k in required}})
    if {c['crate'] for c in commands}!={'dispatch_core','dispatch_harness'}:
        raise ValueError('invocações rustc incompletas; use uma área de build nova')
    return commands

def host():
    result=subprocess.run(['rustc','-vV'],check=True,text=True,capture_output=True,timeout=10)
    return next(line.split(': ',1)[1] for line in result.stdout.splitlines() if line.startswith('host: '))

def stage(source,work):
    shutil.copytree(source,work,ignore=shutil.ignore_patterns('target','.git'))
    shutil.copy(work/'Cargo.lock.txt',work/'Cargo.lock')
    (work/'core/tests').mkdir(exist_ok=True)
    shutil.copy(ROOT/'checks/public.rs',work/'core/tests/public.rs')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/'materials/starter/rust')
    p.add_argument('--build-only',action='store_true')
    a=p.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix='dispatch-check-') as tmp:
            work=Path(tmp)/'rust';stage(a.source,work)
            cargo_home=Path(tmp)/'cargo-home';cargo_home.mkdir()
            target=host()
            for profile in ['inspect0','inspect3']:
                cmd=cargo_command('test',work,profile,target)
                if a.build_only: cmd+=['--no-run']
                print('COMANDO',' '.join(cmd),flush=True)
                r=subprocess.run(cmd,env=environment(cargo_home,profile),cwd=work,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
                print(r.stdout)
                if r.returncode:
                    return 2 if 'could not compile' in r.stdout else 1
                verify_compiler(r.stdout,profile)
                if not a.build_only and 'test result: ok. 2 passed; 0 failed;' not in r.stdout:
                    print('ERRO: testes ausentes');return 2
    except (OSError,ValueError,subprocess.TimeoutExpired) as error:
        print('INCOMPLETO/INFRAESTRUTURA',error);return 2
    print('OK dispatch: build' if a.build_only else 'OK dispatch: vetores, parâmetros e ordem');return 0
if __name__=='__main__':raise SystemExit(main())
