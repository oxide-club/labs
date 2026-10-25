// SPDX-License-Identifier: MIT
package protocol

import "errors"

type Message struct {
	Flags   int
	Payload []byte
}

var ErrArgument = errors.New("argumento fora do contrato")
var ErrTerminal = errors.New("decoder encerrado")

type ProtocolError struct {
	Code      string
	Completed []Message
}

func (e *ProtocolError) Error() string { return e.Code }

func Encode(_ Message) ([]byte, error) {
	// TODO: validar antes de alocar; escrever os oito bytes e copiar payload.
	panic("TODO: implemente validação e encoder")
}

type Decoder struct {
	// TODO: header parcial, payload limitado e estado terminal.
}

func NewDecoder() *Decoder { return &Decoder{} }

func (d *Decoder) Feed(_ []byte) ([]Message, error) {
	// TODO: percorrer chunk sem retê-lo; completar mensagens em ordem.
	panic("TODO: implemente parser incremental")
}

func (d *Decoder) Finish() error {
	panic("TODO: implemente EOF e estado terminal")
}
