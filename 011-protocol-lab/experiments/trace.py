# SPDX-License-Identifier: MIT
"""Imprime somente fronteiras de entrada e mensagens emitidas; não faz parsing."""
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'materials'))
from protocol import Decoder, ProtocolError


def main():
    cases = json.loads((ROOT/'materials/vectors.json').read_text())['valid']
    wire = bytes.fromhex(cases[1]['wire_hex'])
    plans = {'whole': [wire], 'bytes': [wire[i:i+1] for i in range(len(wire))],
             'mixed': [wire[:3],b'',wire[3:8],wire[8:10],wire[10:]],
             'joined': [wire+wire], 'truncated': [wire[:-1]]}
    for name, chunks in plans.items():
        d = Decoder(); print(name)
        for i, chunk in enumerate(chunks):
            out = d.feed(chunk)
            print(i, 'input='+chunk.hex(), 'output='+repr([(m.flags,m.payload.hex()) for m in out]))
        try:
            d.finish(); print('EOF ok')
        except ProtocolError as exc:
            print('EOF '+exc.code)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
