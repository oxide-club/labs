#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Vetores gerados do contrato; não importa nem traduz o parser investigado."""
import argparse
import os
from pathlib import Path
import random
import subprocess

def doc(records=(), checksum=False):
    payload = b''.join(bytes((t, len(data))) + data for t, data in records)
    return b'OXF1' + bytes((int(checksum), len(records))) + len(payload).to_bytes(2, 'little') + payload + (sum(payload).to_bytes(2, 'little') if checksum else b'')

def expected(records=(), checksum=False):
    # Oráculo por construção: calcula do modelo anterior à serialização.
    total = sum(int.from_bytes(data, 'little') for t, data in records if t == 1)
    return f'Ok {int(checksum)} {total} {len(records)}' + ''.join(f' {t}:{data.hex()}' for t, data in records)

def vectors():
    cases = []
    def valid(name, records=(), checksum=False):
        cases.append((name, doc(records, checksum), expected(records, checksum)))
    valid('empty'); valid('empty-checksum', checksum=True)
    valid('maximum-number', [(1, b'\xff\xff')])
    valid('wide-sum', [(1, b'\xff\xff')]*2)
    valid('text-empty', [(2,b'')]); valid('text-32', [(2,b' ~'*16)])
    valid('ordered', [(2,b'ab'),(1,b'\x01\x02'),(2,b'xy')], True)
    # Payload 256, documento 266: sete textos de 32 e um de 16 bytes.
    valid('maximum-document', [(2,b'x'*32)]*7+[(2,b'x'*16)], True)
    valid('count-16', [(1,b'\x00\x01')]*16)
    for name, data, error in [
        ('header', b'OXF', 'Truncated'),
        ('magic', b'NOPE'+doc()[4:], 'BadMagic'),
        ('flags', b'OXF1\x02'+doc()[5:], 'BadFlags'),
        ('count', b'OXF1\x00\x11\x00\x00', 'BadCount'),
        ('payload', b'OXF1\x00\x00\x01\x01', 'BadPayloadLength'),
        ('unknown', doc([(3,b'')]), 'UnknownType'),
        ('numeric-length', doc([(1,b'\x01')]), 'BadRecordLength'),
        ('text-length', doc([(2,b'x'*33)]), 'BadRecordLength'),
        ('low-text', doc([(2,b'\x1f')]), 'BadText'),
        ('high-text', doc([(2,b'\x7f')]), 'BadText'),
        ('checksum', doc(checksum=True)[:-1]+b'\x01', 'BadChecksum'),
        ('trailing', doc()+b'\x00', 'TrailingData'),
        ('missing-record', b'OXF1\x00\x01\x00\x00', {'Truncated', 'BadCount'}),
        ('unconsumed-record', b'OXF1\x00\x00\x02\x00\x02\x00', {'BadCount', 'TrailingData'}),
        ('record-truncated', b'OXF1\x00\x01\x03\x00\x01\x02\x03', 'Truncated'),
        ('too-large', b'\x00'*4097, 'TooLarge'),
    ]: cases.append((name,data,error))
    rng=random.Random(21)
    for i in range(100):
        records=[]
        for _ in range(rng.randrange(7)):
            records.append((1,rng.randrange(65536).to_bytes(2,'little')) if rng.randrange(2) else (2,bytes(rng.randrange(32,127) for _ in range(rng.randrange(33)))))
        valid(f'constructed-{i}',records,bool(i%2))
    return cases

def accepts(want, got):
    return got in want if isinstance(want, set) else got == want

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('runner'); ap.add_argument('--smoke',action='store_true'); args=ap.parse_args()
    cases=vectors()
    if args.smoke: cases=[cases[0], cases[1], cases[4], cases[6]]
    env=dict(os.environ,ASAN_OPTIONS=os.environ.get('ASAN_OPTIONS', 'detect_leaks=1:abort_on_error=1'),UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    failures=0
    # Cada caso roda sozinho; uma falha não esconde outras propriedades.
    for name,data,want in cases:
        try:
            result=subprocess.run([str(Path(args.runner).resolve())],input=data.hex()+'\n',text=True,capture_output=True,timeout=2,env=env)
            good=result.returncode==0 and accepts(want, result.stdout.strip())
            if not good:
                failures+=1; print(f'FAIL {name}: exit={result.returncode} expected={want!r} got={result.stdout.strip()!r}')
                print(result.stderr)
        except subprocess.TimeoutExpired:
            failures+=1; print(f'FAIL {name}: timeout')
    # Mesmos casos intercalados no mesmo processo, inclusive NULL/0.
    sequence=[cases[0],cases[-1],cases[0],('null',b'','Truncated'),cases[-1]]
    result=subprocess.run([str(Path(args.runner).resolve())],input=''.join(data.hex()+'\n' for _,data,_ in sequence),text=True,capture_output=True,timeout=2,env=env)
    if result.returncode or (len(result.stdout.splitlines()) != len(sequence) or not all(accepts(want, got) for (_,_,want),got in zip(sequence,result.stdout.splitlines()))):
        failures+=1; print('FAIL interleaved'); print(result.stderr)
    print(f'cases={len(cases)} interleaved=5 failures={failures}')
    return bool(failures)
if __name__=='__main__': raise SystemExit(main())
