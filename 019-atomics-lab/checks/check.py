# SPDX-License-Identifier: MIT
"""Confira contratos; 0 atendido, 1 propriedade/starter, 2 infraestrutura/exploração interrompida."""
import argparse
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

MARKER = 'PUBLICATION_VIOLATION ready=true data=0 observed=Some(0)'
DIAGNOSTIC = 'RETURN_DIAGNOSTIC variant=Weak observed=Some(0) inferred_ready=true inferred_data=0'

def model_evidence(text, variant):
    summaries=re.findall(r'MODEL_SUMMARY variant=(\w+) executions=(\d+) None=(\d+) Some42=(\d+) Some0=(\d+) Other=(\d+) stop=(\w+)',text)
    if len(summaries)!=1 or summaries[0][0]!=variant:return False
    _,executions,none,some42,some0,other,stop=summaries[0]
    executions,none,some42,some0,other=map(int,(executions,none,some42,some0,other))
    observations=re.findall(r'MODEL_OBSERVATION variant=(\w+) execution=(\d+) observed=(None|Some\(\d+\)) captured_before_join=true',text)
    if len(observations)!=executions or executions!=none+some42+some0+other:return False
    if [(v,int(i)) for v,i,_ in observations]!=[(variant,i) for i in range(1,executions+1)]:return False
    values=[o[2] for o in observations]
    if [values.count('None'),values.count('Some(42)'),values.count('Some(0)')]!=[none,some42,some0]:return False
    config=f'MODEL_CONFIG variant={variant} loom=0.7.2 max_threads=2 max_branches=1000 preemption_bound=none max_permutations=none max_duration=none consumer_before_join=true'
    if text.count(config)!=1 or other:return False
    if variant=='Weak':return some0>0 and stop=='interrupted'
    return none>0 and some42>0 and some0==0 and stop=='complete'

def accepted(result, negative=False, variant=None):
    text = result.stdout
    if variant and not model_evidence(text,variant):return False
    if negative:
        return (result.returncode == 101 and MARKER in text and DIAGNOSTIC in text
                and 'test result: FAILED. 0 passed; 1 failed;' in text)
    return result.returncode == 0 and 'test result: ok. 1 passed; 0 failed;' in text

def failure_kind(text):
    if any(message in text.lower() for message in ['exceeded maximum number of branches', 'model exceeded', 'maximum number of threads', 'loom internal bug']):
        return 2,'EXPLORACAO_INTERROMPIDA: limite ou erro do modelo; propriedade não concluída'
    if 'could not compile' in text or 'error: failed to' in text:
        return 2,'ERRO DE INFRAESTRUTURA/BUILD'
    if 'not yet implemented' in text:return 1,'STARTER_INCOMPLETO'
    if 'MODEL_EVIDENCE_MISSING' in text:return 1,'EVIDENCIA_INSUFICIENTE: publicação não observada no modelo'
    return 1,'PROPRIEDADE_OU_EVIDENCIA_REJEITADA: consulte observações e diagnóstico'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path)
    p.add_argument('--std-only', action='store_true')
    p.add_argument('--build-only', action='store_true')
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    env = {k:v for k,v in os.environ.items() if not k.startswith('LOOM_')}
    with tempfile.TemporaryDirectory(prefix='atomics-check-') as d:
        work = Path(d)/'crate'
        shutil.copytree(a.source or root/'materials/starter', work,
                        ignore=shutil.ignore_patterns('target', '.git'))
        lock = work/'Cargo.lock.txt'
        if lock.exists(): shutil.copy(lock, work/'Cargo.lock')
        (work/'tests').mkdir(exist_ok=True)
        shutil.copy(root/'checks/public.rs', work/'tests/public.rs')
        cmd = ['cargo', 'test', '--locked', '--manifest-path', str(work/'Cargo.toml'), '--test', 'public']
        if not a.std_only: cmd += ['--features', 'model']
        tests = [('sequential_contract',False), ('local_observations',False)] if a.std_only else [
            ('sequential_contract',False), ('release_acquire',False),
            ('sequential_consistency',False), ('weak_counterexample',True)]
        if a.build_only: tests = [(None,False)]
        for name, negative in tests:
            argv = cmd + (['--no-run'] if name is None else [name, '--', '--exact', '--nocapture'])
            print('COMANDO', ' '.join(argv), flush=True)
            try:
                result = subprocess.run(argv, env=env, text=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, timeout=180)
            except (OSError, subprocess.TimeoutExpired) as error:
                print('INCOMPLETO/INFRAESTRUTURA', error); return 2
            print(result.stdout)
            if name is None:
                if result.returncode: return 2
            elif not accepted(result,negative,{'release_acquire':'Publish','sequential_consistency':'Strong','weak_counterexample':'Weak'}.get(name)):
                code,message=failure_kind(result.stdout)
                print(message); return code
    print('OK atomics: build' if a.build_only else 'OK atomics: contratos observados; interpretação ainda necessária')
    return 0

if __name__ == '__main__': raise SystemExit(main())
