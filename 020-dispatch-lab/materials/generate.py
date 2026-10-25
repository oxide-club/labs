# SPDX-License-Identifier: MIT
"""Gere dados CC0; não usa os processadores investigados."""
import argparse
import json
from pathlib import Path
MASK=(1<<64)-1

def values(n):
    # Fórmula por índice; inclui valores acima de i64::MAX e wrap de u64.
    return [((i*0x9e3779b97f4a7c15)^0xd1b54a32d192ed03)&MASK for i in range(n)]

def expected(data):
    # Inteiros ilimitados: aplique o módulo uma vez, após a soma matemática.
    return {'add':(sum(data)+len(data)*7)%(1<<64), 'mul':(sum(data)*3)%(1<<64)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--n',type=int,default=65536);a=p.parse_args()
    if not 0<=a.n<=1000000:p.error('n deve estar entre 0 e 1000000')
    a.out.mkdir(parents=True,exist_ok=False);data=values(a.n)
    (a.out/'dataset.txt').write_text(''.join(f'{v}\n' for v in data))
    (a.out/'expected.json').write_text(json.dumps({'n':a.n,**expected(data)},indent=2)+'\n')
    print('OK dataset',a.n)
if __name__=='__main__':main()
