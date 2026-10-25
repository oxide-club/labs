"""SPDX-License-Identifier: MIT
Execute verificações editoriais declaradas, sem exigir solução no starter.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def run_check(lab, work, check):
    argv=[arg.replace('{work}',str(work)).replace('{lab}',str(lab)) for arg in check['argv']]
    environment=os.environ.copy()
    environment.update(check.get('env',{}))
    try:
        process=subprocess.Popen(argv,cwd=lab,env=environment,stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,text=True,start_new_session=True)
    except OSError as error:
        return {'name':check['name'],'ok':False,'reason':str(error)}
    try:
        stdout,stderr=process.communicate(timeout=check.get('timeout',30))
    except subprocess.TimeoutExpired:
        # Somente o grupo que este runner acabou de criar.
        try: os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        process.communicate()
        return {'name':check['name'],'ok':False,'reason':'timeout'}
    combined=stdout+stderr
    ok=(process.returncode==check.get('status',0)
        and check.get('contains','') in combined
        and not any(text in combined for text in check.get('forbid',[])))
    return {'name':check['name'],'ok':ok,'status':process.returncode,
            'stdout':stdout,'stderr':stderr}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',action='append',help='ID a verificar; pode repetir')
    parser.add_argument('--exclude-lab', action='append', default=[], help='excluir toolchain opcional; pode repetir')
    parser.add_argument('--json',type=Path,help='arquivo para evidências completas')
    args=parser.parse_args()
    config=json.loads((ROOT/'docs/preparation-checks.json').read_text())
    selected=args.lab or list(config)
    unknown=(set(selected) | set(args.exclude_lab))-config.keys()
    if unknown: parser.error('ID sem verificações: '+', '.join(sorted(unknown)))
    selected=[identifier for identifier in selected if identifier not in args.exclude_lab]
    if not selected: parser.error('nenhum laboratório selecionado')
    for identifier in args.exclude_lab: print('IGNORADO por seleção explícita: '+identifier)
    results=[]
    with tempfile.TemporaryDirectory(prefix='oxide-preparation-') as temp:
        for identifier in selected:
            work=Path(temp)/identifier; work.mkdir()
            for check in config[identifier]:
                result=run_check(ROOT/identifier,work,check)
                result['lab']=identifier; results.append(result)
                print(('OK' if result['ok'] else 'FALHOU')+': '+identifier+': '+check['name'])
                if not result['ok']:
                    print(result.get('reason',result.get('stderr','')),file=sys.stderr)
                    # Evite executar etapas dependentes após compilação falhar.
                    break
    if args.json: args.json.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    return any(not result['ok'] for result in results)

if __name__=='__main__':sys.exit(main())
