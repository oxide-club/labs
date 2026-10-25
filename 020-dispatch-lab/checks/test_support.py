# SPDX-License-Identifier: MIT
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'materials'));from generate import expected,values
sys.path.insert(0,str(root/'experiments'));from summarize import summarize
for case in json.loads((root/'materials/fixtures/small.json').read_text()):
    assert expected(case['input'])=={k:case[k] for k in ['add','mul']}
# Segunda formulação: reduza cada resultado individual e acumule módulo u64.
for n in [0,1,17,65536]:
    data=values(n)
    for op in ['add','mul']:
        acc=0
        for x in data:acc=(acc+((x+7) if op=='add' else (x*3))%(1<<64))%(1<<64)
        assert acc==expected(data)[op]
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'sample.csv'
    p.write_text('operation,variant,repetition,n,ns,checksum\nadd,generic,0,4,10,30\nadd,generic,1,4,30,30\n')
    s=summarize(p)[0];assert s['median_ns']==20 and s['median_ns_per_element']==5
    p.write_text('operation,variant,repetition,n,ns,checksum\nadd,generic,0,4,10,30\n')
    try:summarize(p)
    except ValueError:pass
    else:raise AssertionError('dispersão com uma amostra aceita')
print('OK fixtures independentes e dispersão')

from check import environment
import os
for key in ['CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_TARGET','CARGO_BUILD_TARGET_DIR','RUSTC_WRAPPER']:
    os.environ[key]='invalid-test-override'
env=environment()
for key in ['CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_TARGET','CARGO_BUILD_TARGET_DIR','RUSTC_WRAPPER']:
    assert env.get(key,'')==''
assert 'lto=off' in env['CARGO_ENCODED_RUSTFLAGS']
print('OK saneamento de flags, target e wrappers')

from check import verify_compiler, reject_configs

def invocation(crate, opt):
    return f'Running `rustc --crate-name {crate} -C opt-level={opt} -C lto=off -C codegen-units=1 -C debuginfo=2 -C panic=unwind`'
log='\n'.join(invocation(c,'3') for c in ['dispatch_core','dispatch_harness'])
assert len(verify_compiler(log,'inspect3'))==2
assert len(verify_compiler(log+'\nRunning `rustdoc --crate-name dispatch_core --test lib.rs`','inspect3'))==2
for invalid in [log.replace('opt-level=3','opt-level=0'),log.replace('lto=off','lto=fat'),invocation('dispatch_core','3')]:
    try:verify_compiler(invalid,'inspect3')
    except ValueError:pass
    else:raise AssertionError('invocação efetiva divergente aceita')
with tempfile.TemporaryDirectory() as tmp:
    parent=Path(tmp);(parent/'.cargo').mkdir()
    (parent/'.cargo/config.toml').write_text('[profile.inspect3]\nopt-level=0\n')
    try:reject_configs(parent/'child')
    except ValueError:pass
    else:raise AssertionError('config ancestral aceita')
print('OK perfil efetivo, invocações incompletas e config ancestral')
