#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Campanha: reserva antes de iniciar, acerta consumo verificável ao terminar."""
import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('target'); ap.add_argument('corpus'); ap.add_argument('session')
    ap.add_argument('--seconds',type=float); ap.add_argument('--runs',type=int)
    ap.add_argument('--seed',type=int,default=21)
    ap.add_argument('--leaks',choices=['on','off'],default='on')
    a=ap.parse_args()
    if a.seconds is not None and (not math.isfinite(a.seconds) or not 0<a.seconds<=600): ap.error('seconds deve estar em (0, 600].')
    if a.runs is not None and not 1<=a.runs<=1000000: ap.error('runs deve estar em 1..1000000.')
    if not 1<=a.seed<=2147483647: ap.error('seed inválida.')
    target=Path(a.target).resolve(); corpus=Path(a.corpus).resolve(); session=Path(a.session).resolve()
    if not target.is_file() or not corpus.is_dir(): ap.error('Target e corpus devem existir.')
    seeds=sorted(corpus.iterdir())
    if any(not p.is_file() or p.is_symlink() or p.stat().st_size>4096 for p in seeds): ap.error('Corpus deve conter apenas arquivos regulares de até 4096 bytes.')
    session.mkdir(parents=True,exist_ok=True)
    with (session/'lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        statefile=session/'budget.json'
        state=json.loads(statefile.read_text()) if statefile.exists() else {'seconds':0,'runs':0,'attempts':[]}
        seconds=a.seconds if a.seconds is not None else 600-state['seconds']
        runs=a.runs if a.runs is not None else 1000000-state['runs']
        if seconds<=0 or runs<max(2,len(seeds)+1) or state['seconds']+seconds>600 or state['runs']+runs>1000000:
            ap.error('Saldo insuficiente ou reserva acima do contrato (600 s / 1000000 execuções); preserve a sessão.')
        attempt=session/f"attempt-{len(state['attempts'])+1:03d}"
        attempt.mkdir(); artifacts=attempt/'artifacts'; artifacts.mkdir()
        initial=attempt/'corpus-start'; initial.mkdir(); working=attempt/'corpus'; working.mkdir()
        for p in seeds:
            shutil.copyfile(p,initial/p.name); shutil.copyfile(p,working/p.name)
        command=[str(target),str(working),f'-seed={a.seed}',f'-runs={runs}',f'-max_total_time={math.ceil(seconds)}',
                 '-max_len=4096','-timeout=2','-rss_limit_mb=512','-workers=1','-jobs=0','-reload=0',
                 f'-detect_leaks={int(a.leaks=="on")}','-print_final_stats=1',f'-artifact_prefix={artifacts}/']
        env=dict(os.environ,ASAN_OPTIONS=os.environ.get('ASAN_OPTIONS','abort_on_error=1')+f':detect_leaks={int(a.leaks=="on")}',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        record={'phase':'discovery','command':command,'target_sha256':digest(target),
                'corpus_at_attempt_start_sha256':{p.name:digest(initial/p.name) for p in seeds},
                'reserved_seconds':seconds,'reserved_runs':runs,'status':'reserved',
                'ASAN_OPTIONS':env['ASAN_OPTIONS'],'UBSAN_OPTIONS':env['UBSAN_OPTIONS']}
        state['seconds']+=seconds; state['runs']+=runs; state['attempts'].append(record)
        def save():
            temporary=session/'budget.tmp'; temporary.write_text(json.dumps(state,indent=2)+'\n'); temporary.replace(statefile)
        save(); start=time.monotonic(); logpath=attempt/'engine.log'
        with logpath.open('w') as log:
            try:
                result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=seconds)
                code=result.returncode
                record.update(status='completed' if code==0 else 'signaled' if code<0 else 'engine-failure',returncode=code)
                if code<0: record['signal']=signal.Signals(-code).name
            except subprocess.TimeoutExpired:
                record.update(status='wall-time-limit',returncode=124)
            except OSError as error:
                record.update(status='launch-failed',returncode=2,error=str(error))
            finally:
                record['elapsed_seconds']=time.monotonic()-start
                # Uma interrupção do supervisor deixa a reserva inteira debitada.
                save()
        logtext=logpath.read_text(errors='replace')
        counts=re.findall(r'^stat::number_of_executed_units:\s*(\d+)\s*$',logtext,re.M)
        reliable=(len(counts)==1 and 0<int(counts[0])<=runs and record['status'] not in ('wall-time-limit','launch-failed') and 'LeakSanitizer has encountered a fatal error' not in logtext)
        record['accounting']='measured-final-stats' if reliable else 'conservative-reservation'
        record['charged_runs']=int(counts[0]) if reliable else runs
        record['charged_seconds']=min(seconds,record['elapsed_seconds']) if reliable else seconds
        state['runs']+=record['charged_runs']-runs; state['seconds']+=record['charged_seconds']-seconds
        record['corpus_at_attempt_end_sha256']={p.name:digest(p) for p in sorted(working.iterdir()) if p.is_file()}
        record['engine_log_sha256']=digest(logpath); save()
        print(json.dumps(record,indent=2))
        print('Preserve a sessão; o próximo comando sem --runs/--seconds usa o saldo restante.')
        code=record['returncode']; return 128-code if code<0 else code
if __name__=='__main__': raise SystemExit(main())
