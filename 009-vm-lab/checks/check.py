# SPDX-License-Identifier: MIT
"""Oráculos de estado fixos; este arquivo não contém um interpretador."""
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import argparse
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
class ExecutableVM:
    """Transporte do estado abstrato; não implementa validação nem dispatch."""
    def __init__(self, executable):
        self.executable = str(Path(executable).resolve())

    def run(self, source, budget=1000):
        # A API de teste Python distingue '2' de 2; argv não distingue esses tipos.
        # Faixa numérica continua sendo verificada pelo programa do participante.
        if type(budget) is not int:
            raise ValueError('budget deve ser inteiro, sem bool')
        result = subprocess.run([self.executable, str(budget)], input=source,
                                text=True, encoding='utf-8', capture_output=True, timeout=5)
        if result.returncode == 2:
            raise ValueError(result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f'executável: status {result.returncode}: {result.stderr}')
        return json.loads(result.stdout)


def load_python():
    spec = importlib.util.spec_from_file_location('participant_vm', ROOT / 'materials/vm.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vm = None


def state(pc=0, stack=None, steps=0, trace=None, error=None, variables=None):
    return dict(status='error' if error else 'halted', error=error, pc=pc,
                stack=stack or [], variables=variables or [0]*8,
                steps=steps, trace=trace or [])


def row(pc, opcode, stack):
    return dict(pc=pc, opcode=opcode, stack=stack)


def check():
    count = 0
    for case in json.loads((ROOT / 'materials/cases.json').read_text()):
        assert vm.run(case['source']) == case['expected'], case['name']
        count += 1
    # Validação integral, aridade, gramática, faixa e limites textuais.
    invalid = ['', '\n', 'push 1', 'HALT 1', 'PUSH', 'PUSH +1', 'PUSH ١',
               'PUSH 2147483648', 'PUSH -2147483649', 'LOAD -1', 'STORE 8',
               'JMP -1', 'JZ 2\nHALT', 'HALT\nNOPE', 'PUSH 1 # comment',
               'HALT\v', 'HALT\r', 'HALT\n'*257, ' '*16385]
    for source in invalid:
        assert vm.run(source) == state(error='invalid_program'), repr(source)
        count += 1
    # Uma instrução HALT, dois extremos, CRLF e último índice de variável.
    assert vm.run('\nHALT\r\n') == state(steps=1, trace=[row(0,'HALT',[])])
    for number in [-2147483648, 2147483647]:
        assert vm.run(f'PUSH {number}\nHALT') == state(1,[number],2,[row(0,'PUSH',[]),row(1,'HALT',[number])])
    assert vm.run('PUSH -0\nSTORE 7\nLOAD 7\nPOP\nHALT') == state(4,[],5,[row(0,'PUSH',[]),row(1,'STORE',[0]),row(2,'LOAD',[]),row(3,'POP',[0]),row(4,'HALT',[])])
    # Separadores e zeros são parte da gramática, não normalização opcional.
    for source in ['PUSH\t0007\nHALT', 'PUSH   0007\nHALT', '  PUSH \t 0007  \nHALT']:
        assert vm.run(source) == state(1,[7],2,[row(0,'PUSH',[]),row(1,'HALT',[7])]), repr(source)
    assert vm.run('HALT',10000) == state(steps=1,trace=[row(0,'HALT',[])])
    # Salto incondicional e JZ não tomado também consome o topo.
    assert vm.run('JMP 2\nPOP\nHALT') == state(2,[],2,[row(0,'JMP',[]),row(2,'HALT',[])])
    assert vm.run('PUSH 1\nJZ 0\nHALT') == state(2,[],3,[row(0,'PUSH',[]),row(1,'JZ',[1]),row(2,'HALT',[])])
    for opcode in ['POP','STORE 0','JZ 0','ADD','SUB']:
        assert vm.run(opcode) == state(trace=[row(0,opcode.split()[0],[])],error='stack_underflow')
    for op, a, b in [('ADD',2147483647,1),('ADD',-2147483648,-1),('SUB',-2147483648,1),('SUB',2147483647,-1)]:
        assert vm.run(f'PUSH {a}\nPUSH {b}\n{op}\nHALT') == state(2,[a,b],2,[row(0,'PUSH',[]),row(1,'PUSH',[a]),row(2,op,[a,b])], 'integer_overflow')
    for op in ['PUSH 0','LOAD 0']:
        trace=[row(i,'PUSH',[0]*i) for i in range(32)]+[row(32,op.split()[0],[0]*32)]
        assert vm.run('PUSH 0\n'*32+op+'\nHALT') == state(32,[0]*32,32,trace,'stack_overflow')
    assert vm.run('PUSH 0\n'*32+'HALT')['status'] == 'halted'
    assert vm.run('HALT\n'*256)['status'] == 'halted'
    assert vm.run('HALT'+' '*16380)['status'] == 'halted'
    assert vm.run('PUSH 4',1) == state(1,[4],1,[row(0,'PUSH',[])],'pc_out_of_range')
    assert vm.run('JMP 0',3) == state(0,[],3,[row(0,'JMP',[])]*3,'step_limit')
    assert vm.run('PUSH 2\nHALT',1) == state(1,[2],1,[row(0,'PUSH',[])],'step_limit')
    assert vm.run('HALT',1)['status'] == 'halted'
    for budget in [0,-1,10001,True,1.5,'2',None]:
        try:
            vm.run('HALT',budget)
        except ValueError:
            pass
        else:
            raise AssertionError(f'budget inválido aceito: {budget!r}')
    assert vm.run('PUSH 5\nSTORE 0\nPOP') == state(2,[],2,[row(0,'PUSH',[]),row(1,'STORE',[5]),row(2,'POP',[])], 'stack_underflow', [5]+[0]*7)
    # Uma falha não contamina outra chamada.
    vm.run('POP')
    assert vm.run('HALT') == state(steps=1,trace=[row(0,'HALT',[])])
    print(f'OK: {count} casos de fixtures/validação e fronteiras adicionais')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', nargs='?', help='adaptador: budget em argv, fonte em stdin, estado JSON em stdout')
    args = parser.parse_args()
    vm = ExecutableVM(args.executable) if args.executable else load_python()
    try:
        check()
    except Exception as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
