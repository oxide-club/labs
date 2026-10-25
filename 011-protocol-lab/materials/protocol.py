# SPDX-License-Identifier: MIT
"""Starter: implemente framing e parsing conforme index.md."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    flags: int
    payload: bytes


class ProtocolError(Exception):
    def __init__(self, code, completed=None):
        super().__init__(code)
        self.code = code
        self.completed = [] if completed is None else list(completed)


def encode(message: Message) -> bytes:
    raise NotImplementedError('implemente validação e encoder')


class Decoder:
    def __init__(self):
        # Defina aqui o estado incremental.
        pass

    def feed(self, chunk: bytes) -> list[Message]:
        raise NotImplementedError('implemente parser incremental')

    def finish(self) -> None:
        raise NotImplementedError('implemente EOF e estado terminal')
