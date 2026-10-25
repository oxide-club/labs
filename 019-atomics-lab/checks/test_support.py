# SPDX-License-Identifier: MIT
import subprocess
from check import accepted, MARKER, DIAGNOSTIC, model_evidence, failure_kind

def result(code,text): return subprocess.CompletedProcess([],code,text)
def transcript(variant,values,stop):
    text=f'MODEL_CONFIG variant={variant} loom=0.7.2 max_threads=2 max_branches=1000 preemption_bound=none max_permutations=none max_duration=none consumer_before_join=true\n'
    for i,value in enumerate(values,1):text+=f'MODEL_OBSERVATION variant={variant} execution={i} observed={value} captured_before_join=true\n'
    return text+f'MODEL_SUMMARY variant={variant} executions={len(values)} None={values.count("None")} Some42={values.count("Some(42)")} Some0={values.count("Some(0)")} Other=0 stop={stop}\n'
assert not accepted(result(0,'test result: ok. 0 passed; 0 failed;'))
assert not accepted(result(101,'panic genérico'), True)
assert not accepted(result(101,MARKER), True)
assert not accepted(result(101,DIAGNOSTIC+' exceeded maximum number of branches'), True)
assert failure_kind('Model exceeded maximum number of branches')[0]==2
assert failure_kind('not yet implemented')[1]=='STARTER_INCOMPLETO'
assert accepted(result(0,'test result: ok. 1 passed; 0 failed;'))
for variant in ['Publish','Strong']:
    good=transcript(variant,['None','Some(42)'],'complete')
    assert model_evidence(good,variant)
    assert not model_evidence(transcript(variant,['None'],'complete'),variant)
    assert not model_evidence(transcript(variant,['Some(42)'],'complete'),variant)
    assert not model_evidence(good.replace('Some42=1','Some42=2'),variant)
    assert not model_evidence(good.replace('execution=2','execution=1'),variant)
    assert not model_evidence(good.replace('stop=complete','stop=interrupted'),variant)
    assert not model_evidence(good[good.index('MODEL_SUMMARY'):],variant)
weak=transcript('Weak',['None','Some(0)'],'interrupted')+DIAGNOSTIC+MARKER+'test result: FAILED. 0 passed; 1 failed;'
assert accepted(result(101,weak),True,'Weak')
assert not accepted(result(101,weak.replace('captured_before_join=true','captured_before_join=false')),True,'Weak')
print('OK classificação e evidência: vacuidade, contagem incoerente, observações ausentes e interrupção rejeitadas')
