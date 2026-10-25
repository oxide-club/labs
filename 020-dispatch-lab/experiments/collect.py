# SPDX-License-Identifier: MIT
"""Compile e meça em cópia; não publica tabelas nem impõe vencedor."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'));from check import stage,environment,host,cargo_command,verify_compiler,reject_configs
sys.path.insert(0,str(ROOT/'materials'));from generate import values,expected
from summarize import summarize

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/'materials/starter/rust')
    p.add_argument('--dataset',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--repetitions',type=int,default=30);a=p.parse_args()
    if not 2<=a.repetitions<=10000:p.error('repetições: 2..10000')
    a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=False)
    data=[int(line) for line in a.dataset.read_text().splitlines()]
    if any(not 0<=x<1<<64 for x in data):p.error('dataset fora de u64')
    oracle=expected(data);work=a.out/'source';stage(a.source,work)
    reject_configs(work)
    cargo_home=a.out/'cargo-home';cargo_home.mkdir()
    env=environment(cargo_home);target=host()
    commands=[]
    def run(argv,timeout=180,compiler_profile=None):
        commands.append(argv)
        r=subprocess.run(argv,env=env,cwd=work,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
        with (a.out/'commands.log').open('a') as f:
            f.write(json.dumps(argv)+'\n'+r.stdout+r.stderr+f'\nstatus={r.returncode}\n')
        if r.returncode:raise RuntimeError(f'comando falhou ({r.returncode}); consulte commands.log')
        if compiler_profile is not None:
            effective=verify_compiler(r.stderr+'\n'+r.stdout,compiler_profile)
            (a.out/f'{label}.rustc.json').write_text(json.dumps(effective,indent=2)+'\n')
        return r.stdout
    metadata={'platform':platform.platform(),'cpuinfo':Path('/proc/cpuinfo').read_text(),
        'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'n':len(data),'repetitions':a.repetitions,'warmups':2,'order':'rotação por repetição',
        'versions':{tool:run([tool,'--version']) for tool in ['rustc','cargo','objdump','nm','size']},
        'source_sha256':{str(f.relative_to(work)):hashlib.sha256(f.read_bytes()).hexdigest() for f in work.rglob('*') if f.is_file()},
        'flags_by_profile':{p:environment(cargo_home,p)['CARGO_ENCODED_RUSTFLAGS'].split('\x1f') for p in ['inspect0','inspect3']}, 'target':target,
        'affinity':sorted(os.sched_getaffinity(0)),
        'governors':{str(p):p.read_text().strip() for p in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_governor')},
        'frequency_khz_snapshot':{str(p):p.read_text().strip() for p in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_cur_freq')},
        'cargo_config_policy':'fresh CARGO_HOME; ancestral configs refused; critical flags fixed and verified'}
    (a.out/'environment.json').write_text(json.dumps(metadata,indent=2)+'\n')
    for profile in ['inspect0','inspect3']:
        for local in [False,True]:
            label=profile+('-local' if local else '-separate')
            env=environment(cargo_home,profile)
            features=['--features','dispatch-harness/local-core'] if local else []
            # Fresh target directory for each condition makes -vv independently auditable.
            build=cargo_command('build',work,profile,target)
            test=cargo_command('test',work,profile,target)
            for command in [build,test]:
                command[command.index('--target-dir')+1]=str(work/'target'/label)
            run(build+features,compiler_profile=profile)
            tests=run(test+features)
            if 'test result: ok. 2 passed; 0 failed;' not in tests:raise RuntimeError('testes ausentes')
            binary=work/'target'/label/target/profile/'dispatch-harness'
            (a.out/f'{label}.objdump.txt').write_text(run(['objdump','-d','-C',str(binary)]))
            (a.out/f'{label}.nm.txt').write_text(run(['nm','-S','-C',str(binary)]))
            (a.out/f'{label}.size.txt').write_text(run(['size',str(binary)]))
            raw=run([str(binary),str(a.dataset.resolve()),str(a.repetitions)])
            rows=list(csv.DictReader(io.StringIO(raw)))
            wanted={(op,v,i) for op in ['add','mul'] for v in ['generic','dynamic','enum'] for i in range(a.repetitions)}
            got={(r['operation'],r['variant'],int(r['repetition'])) for r in rows}
            if got!=wanted or len(rows)!=len(wanted):raise RuntimeError('coleta incompleta/duplicada')
            for row in rows:
                if int(row['n'])!=len(data) or int(row['checksum'])!=oracle[row['operation']] or int(row['ns'])<0:
                    raise RuntimeError('divergência do oráculo')
            path=a.out/f'{label}.csv';path.write_text(raw)
            (a.out/f'{label}.summary.json').write_text(json.dumps(summarize(path),indent=2)+'\n')
    print('OK coleta: quatro builds; dados brutos, dispersão e inspeção')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as error:
        print('COLETA INCOMPLETA:',error,file=sys.stderr);raise SystemExit(2)
