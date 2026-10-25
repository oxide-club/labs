// SPDX-License-Identifier: MIT
package protocol

import (
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"reflect"
	"testing"
)

type vector struct {
	Name    string `json:"name"`
	Flags   int    `json:"flags"`
	Payload string `json:"payload_hex"`
	Wire    string `json:"wire_hex"`
	Code    string `json:"code"`
}
type vectors struct{ Valid, Invalid, Truncated []vector }

func fixtures(t *testing.T) vectors {
	t.Helper()
	data, err := os.ReadFile("../../vectors.json")
	if err != nil {
		t.Fatal(err)
	}
	var v vectors
	if err := json.Unmarshal(data, &v); err != nil {
		t.Fatal(err)
	}
	return v
}
func unhex(t *testing.T, s string) []byte {
	t.Helper()
	b, err := hex.DecodeString(s)
	if err != nil {
		t.Fatal(err)
	}
	return b
}
func same(t *testing.T, got, want []Message) {
	t.Helper()
	if len(got) != len(want) {
		t.Fatalf("mensagens: %v != %v", got, want)
	}
	for i := range got {
		if got[i].Flags != want[i].Flags || string(got[i].Payload) != string(want[i].Payload) {
			t.Fatalf("mensagem %d: %v != %v", i, got[i], want[i])
		}
	}
}
func protocolError(t *testing.T, err error, code string, completed []Message) {
	t.Helper()
	var pe *ProtocolError
	if !errors.As(err, &pe) || pe.Code != code {
		t.Fatalf("erro %v, esperado %s", err, code)
	}
	same(t, pe.Completed, completed)
}
func terminal(t *testing.T, d *Decoder) {
	t.Helper()
	for _, b := range [][]byte{nil, {}, {1}, make([]byte, 65537)} {
		if _, err := d.Feed(b); !errors.Is(err, ErrTerminal) {
			t.Fatalf("terminal: %v", err)
		}
	}
	if !errors.Is(d.Finish(), ErrTerminal) {
		t.Fatal("Finish após término")
	}
}
func TestFixtures(t *testing.T) {
	v := fixtures(t)
	if len(v.Valid) < 3 || len(v.Invalid) != 8 || len(v.Truncated) != 2 {
		t.Fatal("vetores ausentes")
	}
	for _, c := range v.Valid {
		wire, payload := unhex(t, c.Wire), unhex(t, c.Payload)
		if len(wire) != 8+len(payload) || string(wire[:2]) != "OC" || wire[2] != 1 || int(wire[3]) != c.Flags {
			t.Fatal(c.Name)
		}
		n := uint32(wire[4])<<24 | uint32(wire[5])<<16 | uint32(wire[6])<<8 | uint32(wire[7])
		if int(n) != len(payload) || string(wire[8:]) != string(payload) {
			t.Fatal(c.Name)
		}
	}
}
func TestVectorsAndPartitions(t *testing.T) {
	for _, c := range fixtures(t).Valid {
		t.Run(c.Name, func(t *testing.T) {
			wire := unhex(t, c.Wire)
			msg := Message{c.Flags, unhex(t, c.Payload)}
			encoded, err := Encode(msg)
			if err != nil || string(encoded) != string(wire) {
				t.Fatalf("encode: %x %v", encoded, err)
			}
			plans := [][][]byte{{wire}}
			bytes := [][]byte{}
			for i := range wire {
				bytes = append(bytes, wire[i:i+1])
			}
			plans = append(plans, bytes)
			if len(wire) <= 11 {
				for mask := 0; mask < 1<<(len(wire)-1); mask++ {
					start := 0
					chunks := [][]byte{}
					for i := 1; i < len(wire); i++ {
						if mask&(1<<(i-1)) != 0 {
							chunks = append(chunks, wire[start:i])
							start = i
						}
					}
					plans = append(plans, append(chunks, wire[start:]))
				}
			}
			for _, chunks := range plans {
				d := NewDecoder()
				output := []Message{}
				for _, chunk := range chunks {
					got, err := d.Feed(chunk)
					if err != nil {
						t.Fatal(err)
					}
					output = append(output, got...)
					empty, err := d.Feed(nil)
					if err != nil || len(empty) != 0 {
						t.Fatal("chunk vazio")
					}
				}
				same(t, output, []Message{msg})
				if err := d.Finish(); err != nil {
					t.Fatal(err)
				}
				terminal(t, d)
			}
			for cut := 1; cut < len(wire); cut++ {
				d := NewDecoder()
				got, err := d.Feed(wire[:cut])
				if err != nil || len(got) != 0 {
					t.Fatal("prefixo")
				}
				code := "truncated_payload"
				if cut < 8 {
					code = "truncated_header"
				}
				protocolError(t, d.Finish(), code, nil)
				terminal(t, d)
			}
		})
	}
}
func TestErrorsAndCompleted(t *testing.T) {
	v := fixtures(t)
	first := v.Valid[0]
	good := unhex(t, first.Wire)
	msg := Message{first.Flags, unhex(t, first.Payload)}
	for _, c := range v.Invalid {
		bad := unhex(t, c.Wire)
		for cut := 0; cut < 8; cut++ {
			d := NewDecoder()
			got, err := d.Feed(bad[:cut])
			if err != nil || len(got) != 0 {
				t.Fatal("header parcial")
			}
			got, err = d.Feed(bad[cut:])
			if len(got) != 0 {
				t.Fatal("saída normal em erro")
			}
			protocolError(t, err, c.Code, nil)
			terminal(t, d)
		}
		d := NewDecoder()
		joined := append(append(append([]byte{}, good...), bad...), good...)
		got, err := d.Feed(joined)
		if len(got) != 0 {
			t.Fatal("saída normal em erro")
		}
		protocolError(t, err, c.Code, []Message{msg})
		terminal(t, d)
		d = NewDecoder()
		got, err = d.Feed(good)
		if err != nil {
			t.Fatal(err)
		}
		same(t, got, []Message{msg})
		_, err = d.Feed(bad)
		protocolError(t, err, c.Code, nil)
	}
	for _, c := range v.Truncated {
		d := NewDecoder()
		got, err := d.Feed(unhex(t, c.Wire))
		if err != nil || len(got) != 0 {
			t.Fatal(c.Name)
		}
		protocolError(t, d.Finish(), c.Code, nil)
		terminal(t, d)
	}
}
func TestLimitsOwnershipAndConcatenation(t *testing.T) {
	v := fixtures(t)
	c := v.Valid[1]
	wire := unhex(t, c.Wire)
	msg := Message{c.Flags, unhex(t, c.Payload)}
	joined := append(append([]byte{}, wire...), wire...)
	for cut := 0; cut <= len(joined); cut++ {
		d := NewDecoder()
		a, e := d.Feed(joined[:cut])
		if e != nil {
			t.Fatal(e)
		}
		b, e := d.Feed(joined[cut:])
		if e != nil {
			t.Fatal(e)
		}
		same(t, append(a, b...), []Message{msg, msg})
		if e = d.Finish(); e != nil {
			t.Fatal(e)
		}
	}
	d := NewDecoder()
	if _, e := d.Feed(wire[:5]); e != nil {
		t.Fatal(e)
	}
	if _, e := d.Feed(make([]byte, 65537)); !errors.Is(e, ErrArgument) {
		t.Fatal(e)
	}
	got, e := d.Feed(wire[5:])
	if e != nil {
		t.Fatal(e)
	}
	same(t, got, []Message{msg})
	input := append([]byte{}, wire...)
	d = NewDecoder()
	got, e = d.Feed(input)
	if e != nil {
		t.Fatal(e)
	}
	for i := range input {
		input[i] = 0
	}
	same(t, got, []Message{msg})
	if _, e = d.Feed(wire); e != nil {
		t.Fatal(e)
	}
	if e = d.Finish(); e != nil {
		t.Fatal(e)
	}
	same(t, got, []Message{msg})
	d = NewDecoder()
	if e = d.Finish(); e != nil {
		t.Fatal(e)
	}
	terminal(t, d)
	for _, m := range []Message{{-1, nil}, {2, nil}, {256, nil}, {0, make([]byte, 4097)}} {
		if _, e := Encode(m); !errors.Is(e, ErrArgument) {
			t.Fatalf("encode inválido: %v", e)
		}
	}
	maxChunk := []byte{}
	empty := unhex(t, v.Valid[0].Wire)
	for i := 0; i < 8192; i++ {
		maxChunk = append(maxChunk, empty...)
	}
	d = NewDecoder()
	many, e := d.Feed(maxChunk)
	if e != nil || len(many) != 8192 {
		t.Fatalf("chunk máximo: %d %v", len(many), e)
	}
	a := NewDecoder()
	b := NewDecoder()
	_, e = a.Feed(wire[:5])
	if e != nil {
		t.Fatal(e)
	}
	bg, e := b.Feed(wire)
	if e != nil {
		t.Fatal(e)
	}
	ag, e := a.Feed(wire[5:])
	if e != nil {
		t.Fatal(e)
	}
	if !reflect.DeepEqual(ag, bg) {
		t.Fatal("instâncias compartilham estado")
	}
}

// O chamador pode reutilizar cada chunk logo após Feed, inclusive um fragmento.
func TestPartialChunkOwnership(t *testing.T) {
 c := fixtures(t).Valid[1]
 wire := unhex(t, c.Wire)
 msg := Message{c.Flags, unhex(t, c.Payload)}
 for cut := 1; cut < len(wire); cut++ {
  d := NewDecoder()
  input := append([]byte{}, wire[:cut]...)
  got, err := d.Feed(input)
  if err != nil || len(got) != 0 { t.Fatal("fragmento parcial", err) }
  for i := range input { input[i] ^= 0xff }
  got, err = d.Feed(wire[cut:])
  if err != nil { t.Fatal("fragmento alterado pelo chamador", err) }
  same(t, got, []Message{msg})
  if err = d.Finish(); err != nil { t.Fatal(err) }
 }
}
