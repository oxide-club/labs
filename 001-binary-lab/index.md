---
title: Laboratório de Representação Binária
area: binary-reverse-engineering
slug: 001-binary-lab
summary: Implemente um header de 32 bits e sua representação externa little-endian.
question: Como campos lógicos viram bits de uma palavra e bytes de um formato externo?
draft: false
publishedAt: 2026-10-25
topics: [Representação binária, Operadores bitwise, Endianness]
prerequisites: [Funções em C, Arrays, Inteiros sem sinal, Hexadecimal]
tools: [GCC ou Clang]
environment: C11 com bytes de oito bits e inteiros uint32_t e uint8_t
difficulty: intermediate
---

## O que vamos investigar

Um campo lógico, uma palavra numérica e uma sequência de bytes têm contratos
diferentes. Você implementará `header_pack`, `header_unpack`, `store_le32` e
`load_le32` em C11. O layout de `Header` na memória não define a serialização.

### Contrato do núcleo

| Campo | Bits da palavra | Largura | Valores aceitos |
| --- | --- | ---: | --- |
| version | 31 a 29 | 3 | 0 a 7 |
| type | 28 a 24 | 5 | 0 a 31 |
| flags | 23 a 20 | 4 | 0 a 15 |
| length | 19 a 0 | 20 | 0 a 1048575 |

Todos esses valores são válidos. `length` é apenas um número; não exige payload.
Os quatro bytes externos seguem little-endian em qualquer máquina.

A API está em [packet.h](materials/starter/packet.h). `header_pack` retorna `false`
se qualquer ponteiro for nulo ou qualquer campo estiver fora da faixa. Se `out`
for válido, a falha deve preservar seu valor anterior. `header_unpack` recebe
um `Header *` válido e deve decodificar qualquer palavra de 32 bits.
`store_le32` e `load_le32` recebem uma região válida de quatro bytes.
Os argumentos de entrada e saída de cada operação não se sobrepõem.
A conversão deve usar bytes e campos explícitos.

## Antes de começar

### Linguagens e ambiente

Referência: **C11**. Aceitas: Livre; por exemplo C, Rust, Go e Python.
Recomendadas: Rust, Go e Python. Bytes de 8 bits; palavra sem sinal de 32 bits; conversão explícita de campos e bytes.
Materiais oficiais: C11 existente.
Equivalência: equivalente sob contrato adaptado.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

Você deve conhecer funções, arrays, condições, inteiros sem sinal, hexadecimal e
os operadores bitwise `&`, `|`, `^`, `<<` e `>>`. Instale GCC ou Clang e use um
terminal. O [guia dos materiais](materials/README.md) contém os comandos completos
para compilar, executar os checks e observar a representação do host.

Não aplique as funções que exigem quatro bytes a buffers menores. Ponteiros nulos
só são entradas a rejeitar em `header_pack`; as outras funções têm pré-condições.

## Materiais

- [Starter](materials/starter/packet.c): corpos incompletos das quatro funções.
- [Checks públicos](materials/checks/tests.c): vetores, limites, falhas e ida e volta.
- [Fixtures](materials/fixtures/vectors.csv): os quatro vetores do contrato original.
- [Experimento](materials/experiments/observe.c): palavra, bytes do host e bytes externos.
- [Guia autocontido](materials/README.md): contrato e instruções de execução.
- [Modelo de relato](report-template.md): roteiro para registrar evidências.

## Etapas da investigação

1. **Prever.** Desenhe as faixas de bits de dois vetores. Sem executar código,
   calcule suas palavras e seus bytes. Guarde o raciocínio antes de consultar a tabela.
2. **Observar.** Consulte os [vetores conhecidos](materials/fixtures/vectors.csv).
   Compile o starter e execute os checks. Registre status, primeira falha e contagem.
   A compilação deve funcionar; o starter deve falhar nos testes de funcionalidade.
3. **Explicar.** Justifique a posição de cada campo e a ordem dos quatro bytes.
   Explique por que truncar campos inválidos contraria o contrato e por que a saída
   precisa permanecer intacta em uma falha.
4. **Implementar.** Complete `packet.c`, sem alterar a API, sem usar o layout da
   `struct` como formato externo e sem fornecer payload. Crie também seus testes.
5. **Verificar.** Execute os checks e acrescente combinações válidas próprias.
   Rode o experimento e compare host e formato externo. Explique por que dois
   componentes com o mesmo erro podem passar em ida e volta, mas falhar nos vetores.

## Critérios de conclusão

Execute também o build com UndefinedBehaviorSanitizer do guia; ele deve terminar com status zero e sem `runtime error`.

Entregue `packet.h`, `packet.c`, seus testes e o relato. Os checks públicos devem
terminar com status zero e zero falhas após sua implementação. Demonstre os quatro
vetores, decodificação, rejeições individuais de 8/32/16/1048576 nos campos
respectivos, preservação de `0xA5A5A5A5`, nulos de `header_pack` e ida e volta.
Compare campos individualmente; igualdade dos bytes de uma `struct` não define
igualdade entre headers. Explique a separação entre palavra e bytes e registre
o ambiente. A execução dos checks complementa a explicação; não prova correção geral.

## Extensões opcionais

Acrescente `uint32_t rotate_left32(uint32_t word, unsigned n)` e
`unsigned count_bits32(uint32_t word)`. A rotação aceita `0 <= n < 32`, incluindo
zero; a contagem retorna o total de bits iguais a um. A tabela completa fica no
[guia dos materiais](materials/README.md). Essas funções não fazem parte do núcleo.

## Participação no clube

Compartilhe uma tentativa com hipótese, comando, entrada e resultado observado.
Ao pedir ajuda, indique o primeiro vetor que falha e a explicação que tentou.
Evite publicar uma solução completa na discussão inicial. Melhorias nos checks
devem citar o requisito do contrato que passam a verificar.

## Referências e atividades relacionadas

Leia as [referências orientadas](references.md) após investigar o núcleo: C11 para
regras de deslocamento, Protobuf para leitura com limites e Linux para campos de
rede. A representação binária prepara a leitura de object files, protocolos e
metadados de alocadores. A inspiração temática vem do Data Lab de CS:APP;
o formato e a API usados aqui pertencem ao caderno do Oxide Club.
