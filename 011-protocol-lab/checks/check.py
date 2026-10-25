# SPDX-License-Identifier: MIT
"""Vetores externos são o oráculo principal; roundtrip é complementar."""
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'materials'))
from protocol import Message, ProtocolError, Decoder, encode


def expect_error(cls, action, code=None, completed=None):
    try:
        action()
    except cls as exc:
        if code is not None:
            assert exc.code == code, (exc.code, code)
            assert exc.completed == ([] if completed is None else completed)
        return exc
    raise AssertionError(f'esperado {cls.__name__}: {code}')


def terminal(d):
    for chunk in (b'', b'junk', None):
        expect_error(RuntimeError, lambda: d.feed(chunk))
    expect_error(RuntimeError, d.finish)


def partitions(data):
    # Todas as 2**(N-1) divisões em chunks não vazios, não apenas um corte.
    for mask in range(1 << (len(data)-1)):
        start = 0
        chunks = []
        for i in range(1, len(data)):
            if mask & (1 << (i-1)):
                chunks.append(data[start:i]); start = i
        yield chunks + [data[start:]]


def check():
    vectors = json.loads((ROOT/'materials/vectors.json').read_text())
    valid = []
    for case in vectors['valid']:
        msg = Message(case['flags'], bytes.fromhex(case['payload_hex']))
        wire = bytes.fromhex(case['wire_hex'])
        valid.append((wire, msg))
        assert encode(msg) == wire, case['name']
        plans = partitions(wire) if len(wire) <= 11 else ([wire], [wire[i:i+1] for i in range(len(wire))])
        for chunks in plans:
            d = Decoder(); output = []
            assert d.feed(b'') == []
            for chunk in chunks:
                output += d.feed(chunk)
                assert d.feed(b'') == []
            assert output == [msg], case['name']
            assert d.finish() is None
            terminal(d)
        # Todo prefixo próprio da mensagem máxima e das mensagens pequenas.
        for cut in range(1, len(wire)):
            d = Decoder()
            assert d.feed(wire[:cut]) == []
            code = 'truncated_header' if cut < 8 else 'truncated_payload'
            expect_error(ProtocolError, d.finish, code)
            terminal(d)
        d = Decoder()
        assert d.feed(encode(msg)) == [msg]  # propriedade adicional
        d.finish()
    for case in vectors['truncated']:
        d = Decoder()
        assert d.feed(bytes.fromhex(case['wire_hex'])) == []
        expect_error(ProtocolError, d.finish, case['code'])
        terminal(d)
    small, empty = valid[0]; binary, bm = valid[1]
    joined = small + binary + small
    # Todos os cortes em dois chunks da concatenação, incluindo chunks vazios.
    for cut in range(len(joined)+1):
        d = Decoder()
        assert d.feed(joined[:cut]) + d.feed(joined[cut:]) == [empty, bm, empty]
        d.finish()
    d = Decoder()
    assert d.feed(small*8192) == [empty]*8192  # chunk exato de 65536
    d.finish()
    for case in vectors['invalid']:
        wire = bytes.fromhex(case['wire_hex'])
        for cut in range(9):
            d = Decoder()
            if cut < 8:
                assert d.feed(wire[:cut]) == []
                expect_error(ProtocolError, lambda: d.feed(wire[cut:]), case['code'])
            else:
                expect_error(ProtocolError, lambda: d.feed(wire), case['code'])
            terminal(d)
        d = Decoder()
        expect_error(ProtocolError, lambda: d.feed(small+binary+wire+small), case['code'], [empty,bm])
        terminal(d)
        # Mensagens retornadas em uma chamada anterior não reaparecem no erro.
        d = Decoder(); assert d.feed(small) == [empty]
        expect_error(ProtocolError, lambda: d.feed(wire), case['code'])
    for value in (None, '', bytearray(), memoryview(b''), 1):
        d = Decoder(); assert d.feed(binary[:5]) == []
        expect_error(TypeError, lambda: d.feed(value))
        assert d.feed(binary[5:]) == [bm]
    d = Decoder(); assert d.feed(binary[:5]) == []
    expect_error(ValueError, lambda: d.feed(b'x'*65537))
    assert d.feed(binary[5:]) == [bm]
    d.finish(); terminal(d)
    d = Decoder(); assert d.finish() is None; terminal(d)
    for value in (None, {}, (0,b'')):
        expect_error(TypeError, lambda: encode(value))
    for flags in (True, 0.0, '0', None):
        expect_error(TypeError, lambda: encode(Message(flags,b'')))
    for payload in ('', bytearray(), memoryview(b''), None):
        expect_error(TypeError, lambda: encode(Message(0,payload)))
    class BytesSubclass(bytes):
        pass
    class MessageSubclass(Message):
        pass
    class IntSubclass(int):
        pass
    expect_error(TypeError, lambda: encode(MessageSubclass(0,b'')))
    expect_error(TypeError, lambda: encode(Message(IntSubclass(0),b'')))
    expect_error(TypeError, lambda: encode(Message(0,BytesSubclass(b''))))
    expect_error(TypeError, lambda: Decoder().feed(BytesSubclass(b'')))
    expect_error(TypeError, lambda: encode(Message(2,None)))
    for flags in (-1,2,255,256):
        expect_error(ValueError, lambda: encode(Message(flags,b'')))
    expect_error(ValueError, lambda: encode(Message(0,b'x'*4097)))
    # Independência e lifetime dos retornos.
    d = Decoder(); result = d.feed(binary)
    other = Decoder(); assert other.feed(small) == [empty]
    assert d.feed(small) == [empty]
    d.finish(); assert result == [bm]
    print('PASS: vetores, fragmentações, concatenação, limites, EOF e estados')


if __name__ == '__main__':
    try:
        check()
    except Exception as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
