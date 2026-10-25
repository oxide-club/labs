---
title: Laboratório de Protocolos Binários
slug: 011-protocol-lab
summary: Implemente framing incremental com limites e erros explícitos.
question: Como reconhecer mensagens em fragmentos arbitrários de bytes?
draft: false
publishedAt: 2026-10-25
topics: [Protocolos, Framing, Parsers]
prerequisites: [Bytes, Inteiros, Funções, Estado]
tools: [Python 3]
environment: Python 3.10 ou superior e biblioteca padrão em Linux
difficulty: intermediate
---

## O que vamos investigar

Um fluxo preserva a ordem dos bytes, mas uma leitura não define uma mensagem.
Framing é a identificação das fronteiras das mensagens nesse fluxo.
Implemente manualmente encoder e decoder incremental, sem gerador de protocolo.

### Contrato técnico

O formato externo tem header fixo de oito bytes. Os offsets começam em zero.

| Offset | Tamanho | Campo e valor |
| --- | --- | --- |
| 0 | 2 | magic: bytes hexadecimais `4f 43` |
| 2 | 1 | version: exatamente 1 |
| 3 | 1 | flags: somente 0 ou 1; bit 0 é marcador opaco, sem transformar payload |
| 4 | 4 | length: inteiro sem sinal big-endian, de 0 a 4096 |
| 8 | length | payload: bytes opacos, inclusive zero e bytes não UTF-8 |

Não há padding, checksum, terminador ou alinhamento implícito. O comprimento exclui o header.
Bytes após uma mensagem iniciam o próximo header; não são descartados.

Na versão Python, a API de `materials/protocol.py` usa `Message(flags, payload)`, dataclass frozen com campos nessa ordem.
O construtor apenas armazena campos; a validação ocorre em `encode(message) -> bytes`.
Aceite somente `type(message) is Message`, `type(flags) is int` e `type(payload) is bytes`.
Tipos diferentes, inclusive bool, subclasses, bytearray e memoryview, geram `TypeError`.
Valide tipos na ordem message, flags, payload; depois valide o valor de flags e o tamanho do payload, nessa ordem.
Flags fora de {0,1} e payload maior que 4096 geram `ValueError`. Payload vazio é válido.
O encoder não mantém estado e deve validar antes de copiar o payload.

`Decoder()` começa ativo, sem bytes pendentes. `feed(chunk: bytes) -> list[Message]` aceita somente o tipo exato bytes.
Cada chunk tem no máximo 65536 bytes; acima disso gere `ValueError` antes de processar qualquer byte.
Tipo inválido gera `TypeError`. Esses dois erros de argumento preservam estado e não são erros de protocolo.
`feed(b'')` ativo retorna [] e preserva qualquer fragmento; não significa EOF.
Uma chamada pode retornar zero, uma ou várias mensagens em ordem. Preserve os fragmentos entre chamadas.

Valide o header somente quando seus oito bytes estiverem disponíveis, antes de acumular o payload.
Se vários campos forem inválidos, a precedência é magic, version, flags, length.
Gere `ProtocolError` com atributo `code` igual a `bad_magic`, `bad_version`, `bad_flags` ou `oversize`.
Se o chunk contém mensagens válidas antes do erro, não retorne normalmente: inclua essas mensagens em `exc.completed`.
Esse atributo é uma lista nova e contém somente mensagens concluídas nesta chamada, uma única vez.
Descarte o fragmento inválido e o restante do chunk. O decoder entra em estado terminal de falha.
Não procure outra magic para tentar recuperar o fluxo.

`finish() -> None` declara EOF. Se ativo e sem fragmento, encerre com sucesso.
Se restam 1 a 7 bytes do header, gere `ProtocolError('truncated_header')`.
Se o header válido está completo e falta payload, gere `ProtocolError('truncated_payload')`.
Nesses erros `completed` é []; descarte pendências e entre em falha terminal.
Após sucesso ou falha terminal, qualquer `feed`, mesmo vazio ou mal tipado, e qualquer `finish` geram `RuntimeError` antes de validar argumentos.
Não existe reset; crie outro Decoder para outro fluxo. Instâncias não compartilham estado.

`ProtocolError` deriva de Exception e recebe `(code, completed=None)`; completed ausente significa [].
Mensagens e payloads retornados devem permanecer válidos após chamadas posteriores.
O decoder não deve reter referências ao chunk nem às mensagens já entregues.
Retenha no máximo 4104 bytes de dados de protocolo entre chamadas; após erro ou EOF, retenha zero.
Processe chunks por posição: não acumule o chunk inteiro em um buffer sem limite.
Valide length antes de reservar/copiar payload. Copie cada byte de entrada no máximo um número constante de vezes; não reconstrua o prefixo acumulado a cada byte.
A lista de saída pode crescer com o número de mensagens do chunk; esse espaço e o objeto de entrada pertencem ao custo da chamada, separado do estado persistente.
Os checks funcionais não demonstram esses limites: revise o código e justifique suas cópias no relato.

## Antes de começar

### Linguagens e ambiente

Referência: **Python**. Aceitas: Livre; por exemplo C, Rust, Go e Python.
Recomendadas: Rust, Go e Python. Header de oito bytes; length uint32 big-endian até 4096; parsing incremental próprio.
Materiais oficiais: Python existente; Go: `materials/starter/go/`.
Equivalência: equivalente sob contrato adaptado.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

Conheça bytes, slicing, inteiros de largura fixa e exceções. Use Python 3.10+ com biblioteca padrão.
Leia [o guia local](README.md). Os comandos partem deste diretório; não é necessário abrir sockets.

## Materiais

[O guia de materiais](materials/README.md) descreve o starter e os [vetores](materials/vectors.json).
[Os checks](checks/check.py) usam bytes canônicos independentes do encoder.
[O experimento](experiments/fragmentation.md) compara fragmentação e concatenação.

## Etapas da investigação

1. **Prever:** marque os oito bytes de header nos vetores empty e binary. Preveja os retornos de chunks de um byte.
2. **Observar:** leia o trace normativo do experimento. Identifique quando length passa a estar disponível.
3. **Explicar:** explique por que bytes disponíveis e mensagens completas são contagens diferentes. Relacione EOF ao estado pendente.
4. **Implementar:** complete encode, feed e finish. Registre invariantes, precedência de erros e limites de memória.
5. **Verificar:** execute os checks e o experimento. Compare o trace observado com sua previsão, incluindo mensagens anteriores a um erro.

## Critérios de conclusão

Os checks devem terminar com status zero. Entregue implementação, trace de três fragmentações e dois casos inválidos explicados.
Justifique a independência dos vetores, o tratamento de EOF e o limite de memória antes de fazer allocation.
Explique por que roundtrip sozinho aceita bugs simétricos e por que um read de socket não equivale a uma mensagem.
Os checks públicos cobrem casos finitos; não provam correção geral nem custo assintótico.

## Extensões opcionais

Você pode adicionar checksum, fuzzing ou outra versão em uma API separada.
Especifique os novos bytes e a compatibilidade antes de implementar. Preserve o contrato obrigatório.

## Participação no clube

Compartilhe bytes em hexadecimal, fronteiras dos chunks, resultado previsto e observado.
Use [o modelo de relato](report-template.md). Inclua o menor fluxo que reproduz a divergência.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md). Relacione framing à representação binária e à leitura parcial em pipes.
EOF de transporte é uma observação externa; o experimento usa finish para representá-lo explicitamente.
