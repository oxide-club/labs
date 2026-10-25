# SPDX-License-Identifier: MIT
"""Checks públicos: executar da raiz do laboratório, após make -C materials."""
from pathlib import Path
import os
import platform
import subprocess
import sys
b = Path(__file__).resolve().parents[1] / 'materials/build'
def run(args, env=None):
    return subprocess.run([str(x) for x in args], capture_output=True, text=True, timeout=5, env=env)
failures = 0
def check(label, condition):
    global failures
    print(('PASS ' if condition else 'FAIL ') + label)
    failures += not condition
for name in ('archive-client','shared-client'):
    p = run([b/name])
    check(name, p.returncode == 0 and p.stdout == '7 25\n')
for name, code in [('no-such.so',3), ('renamed.so',4), ('liboxide.so',0)]:
    p = run([b/'dynamic', b/name, 'oxide_add', 'now','call'])
    check(name, p.returncode == code and (p.stdout == '7\n' if code == 0 else p.stdout == '' and p.stderr.startswith('open:' if code == 3 else 'symbol:')))
p = run([b/'dynamic',b/'liboxide.so','absent','now','call'])
check('símbolo ausente', p.returncode == 4 and p.stdout == '' and p.stderr.startswith('symbol:'))
p = run([b/'dynamic',b/'liboxide.so','oxide_add','lazy','skip'])
check('skip', p.returncode == 0 and p.stdout == '')
for args in ([], [b/'liboxide.so','oxide_add','invalid','call'],
             [b/'liboxide.so','oxide_add','now','invalid'],
             [b/'liboxide.so','oxide_add','now','call','extra'],
             [b/'liboxide.so','oxide_add','now']):
    p = run([b/'dynamic', *args])
    check('CLI ' + repr(args), p.returncode == 2 and p.stdout == '' and bool(p.stderr))
p = run([b/'dynamic',b/'liboxide.so','absent','now','skip'])
check('skip sem busca de símbolo', p.returncode == 0 and p.stdout == '')
p = run([b/'dynamic',b/'broken.so','oxide_add','now','skip'])
check('NOW resolve referência antes de skip', p.returncode == 3 and p.stdout == '' and p.stderr.startswith('open:'))
# run sempre cria outro processo; nenhum objeto broken é carregado no Python dos checks.
p = run([b/'dynamic',b/'broken.so','oxide_add','lazy','skip'])
libc = platform.libc_ver()
eager = bool(os.environ.get('LD_BIND_NOW'))
print('ENV libc=', libc, 'LD_BIND_NOW=', eager,
      'LD_PRELOAD=', bool(os.environ.get('LD_PRELOAD')))
if libc[0] == 'glibc' and not os.environ.get('LD_PRELOAD'):
    expected = 3 if eager else 0
    check('LAZY/skip glibc conforme ambiente', p.returncode == expected and p.stdout == ''
          and (not expected or p.stderr.startswith('open:')))
else:
    check('LAZY/skip resultado permitido pelo loader', p.stdout == '' and
          (p.returncode == 0 or p.returncode == 3 and p.stderr.startswith('open:')))
    print('OBS LAZY/skip:', p.returncode, repr(p.stderr))
for action, symbol, code, output in [
    ('call','oxide_add',0,'fixture-closed\n7\n'),
    ('skip','oxide_add',0,'fixture-closed\n'),
    ('call','absent',4,'fixture-closed\n')]:
    p = run([b/'dynamic-lifetime',b/'lifetime.so',symbol,'now',action])
    check('lifetime '+action+'/'+symbol, p.returncode == code and p.stdout == output
          and p.stderr.count('fixture-close-call\n') == 1)
for symbol, code in [('oxide_add',5),('absent',4)]:
    env = dict(os.environ, OXIDE_TEST_CLOSE_FAIL='1')
    p = run([b/'dynamic-lifetime',b/'liboxide.so',symbol,'now','call'],env=env)
    check('falha de close '+symbol, p.returncode == code and p.stdout == ''
          and p.stderr.count('fixture-close-call\n') == 1 and 'close:' in p.stderr
          and (symbol != 'absent' or 'symbol:' in p.stderr))
sys.exit(bool(failures))
