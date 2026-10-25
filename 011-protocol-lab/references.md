# Referências orientadas — Protocolos Binários

## Código real verificado

[Redis 7.4.0 — networking.c](https://github.com/redis/redis/blob/7.4.0/src/networking.c)
implementa entrada de clientes, parsing RESP e controle de buffers.
A [fonte raw](https://raw.githubusercontent.com/redis/redis/7.4.0/src/networking.c) foi consultada em 25/10/2026.
Observe `processMultibulkBuffer`, `processInputBuffer` e `readQueryFromClient`.
Compare a validação de `proto_max_bulk_len` com a reserva de espaço posterior.
RESP usa comprimentos textuais e múltiplos argumentos; este laboratório usa header binário fixo.
Pergunta: qual estado permite parar por falta de bytes e continuar após outra leitura?

[Protocol Buffers — coded_stream.cc](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/io/coded_stream.cc)
implementa leituras codificadas e limites de buffers em C++.
A [fonte raw](https://raw.githubusercontent.com/protocolbuffers/protobuf/main/src/google/protobuf/io/coded_stream.cc) foi consultada em 25/10/2026.
Observe `ReadRaw`, `ReadStringFallback`, `PushLimit` e `ReadVarint64Slow`.
ReadRaw cruza buffers por cópia e Refresh; PushLimit verifica limites antes de somar posições.
Protobuf inclui varints e campos tipados, diferentes do payload opaco do exercício.
Pergunta: por que esgotar um buffer não equivale necessariamente a terminar uma mensagem?

Limite de reprodução: a referência Redis usa tag; Protobuf usa branch móvel.
As tentativas de acessar Protobuf v28.3 e v25.3 e de resolver tags pela API GitHub falharam nesta preparação.
Não foi possível registrar SHA verificado. Confirme a revisão antes de comparar linhas em outra data.
Nenhum trecho dessas fontes foi incorporado ao starter.

## Leituras de apoio do currículo

[Beej — Guide to Network Programming](https://beej.us/guide/bgnet/) ajuda a estudar leituras parciais e representação de inteiros.
[RFC 4506 — XDR](https://www.rfc-editor.org/rfc/rfc4506) apresenta outro contrato de representação externa.
Essas leituras são complementares; o formato obrigatório está no [enunciado](index.md).
O roteiro curricular também indica Zhirkov, capítulos 1 e 11, e CS:APP, capítulo 10.
Esses livros não foram consultados nesta preparação e não são necessários para executar o pacote.
