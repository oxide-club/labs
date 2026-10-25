---
title: Laboratório de Representação Binária
area: data-protocols
slug: 001-binary-lab
summary: Implemente um header de 32 bits e sua representação externa little-endian.
question: Como campos lógicos viram bits de uma word e bytes de um formato externo?
draft: false
publishedAt: 2026-10-25
topics: [Representação binária, Operadores bitwise, Endianness]
prerequisites: [Funções em C, Arrays, Unsigned integers, Hexadecimal]
tools: [GCC ou Clang]
environment: C11 com bytes de oito bits e inteiros uint32_t e uint8_t
difficulty: intermediate
---

## O que vamos investigar

### O que você vai construir

Você vai construir **um encoder e um decoder de um header binário
de quatro bytes**. Imagine que um programa precisa guardar ou transmitir quatro
informações: `version`, `type`, `flags` e `length`. Sua tarefa é reunir esses
campos em um inteiro de 32 bits, escrever esse inteiro em quatro bytes e fazer
o caminho inverso para recuperar as informações originais.

Os mesmos dados terão três representações:

```text
Campos (Header)              Inteiro de 32 bits         Quatro bytes

version = 1
type    = 2    ──pack──▶      0x22500102    ──store──▶   02 01 50 22
flags   = 5    ◀─unpack─                   ◀──load───
length  = 258
```

Neste enunciado, **word** significa o inteiro de 32 bits. **Formato externo**
é a sequência de quatro bytes que poderia ser gravada em um arquivo ou enviada
a outro programa. O exercício trabalha essas conversões em memória; não exige
implementar envio pela rede ou gravação em arquivo.

Os nomes dos campos dão contexto ao exercício. `length=258`, por exemplo, é
apenas um número: você não precisa criar uma mensagem com 258 bytes nem fornecer
seu conteúdo (payload).

#### As quatro funções que você deve implementar

O código inicial em [packet.c](materials/starter/packet.c) contém quatro funções
incompletas. Complete seus corpos mantendo as assinaturas de
[packet.h](materials/starter/packet.h):

| Função | Entrada | Resultado esperado |
| --- | --- | --- |
| `header_pack` | Um `Header` com os quatro campos | Validar os campos, reuni-los em uma word de 32 bits e indicar sucesso ou falha. |
| `header_unpack` | Uma word de 32 bits | Separar a word e escrever os quatro campos em um `Header`. |
| `store_le32` | Uma word de 32 bits | Escrever sua representação little-endian em um array de quatro bytes. |
| `load_le32` | Um array de quatro bytes little-endian | Reconstruir e retornar a word de 32 bits. |

### Como representar os dados

#### Dos campos para a word

Cada campo ocupa uma parte fixa do inteiro. As posições são numeradas de 0 a 31,
com o bit menos significativo na posição zero:

```text
bits:  31 a 29 | 28 a 24 | 23 a 20 | 19 a 0
       version    type     flags     length
        3 bits   5 bits    4 bits    20 bits
```

Use shifts para posicionar os valores e operações bitwise para combinar
ou extrair os campos. Os espaços reservados somam 32 bits e determinam os
intervalos aceitos:

| Campo | Bits da word | Largura | Valores aceitos |
| --- | --- | ---: | --- |
| version | 31 a 29 | 3 | 0 a 7 |
| type | 28 a 24 | 5 | 0 a 31 |
| flags | 23 a 20 | 4 | 0 a 15 |
| length | 19 a 0 | 20 | 0 a 1048575 |

Todos os valores nos intervalos da tabela são válidos. No exemplo acima,
`version=1` ocupa os três bits superiores e `length=258` ocupa os vinte bits
inferiores. Com `type=2` e `flags=5` nas posições indicadas, a word resultante
é `0x22500102`.

#### Da word para os bytes

**Little-endian significa escrever primeiro o byte menos significativo.**
Por isso, a word `0x22500102` deve produzir este array:

```text
índice:    0    1    2    3
byte:     02   01   50   22
```

Essa ordem é uma regra do formato externo e deve ser a mesma em qualquer máquina.
A posição dos campos no valor numérico também é fixa; a endianness da máquina
descreve como ela representa esse valor na memória.

Faça a conversão por campos e bytes explícitos. Copiar diretamente a memória da
`struct Header` não implementa o formato: a struct guarda quatro campos
`uint32_t`, enquanto a representação externa reúne todos eles em quatro bytes.
O layout de `Header` na memória não define a serialização.

#### Validação e condições de uso

A API está em [packet.h](materials/starter/packet.h). `header_pack` retorna `false`
se qualquer pointer for null ou um campo estiver fora do intervalo permitido
na tabela. Por exemplo, `version` aceita valores de 0 a 7; o valor 8 deve ser
rejeitado, pois não cabe nos três bits reservados para esse campo.

Em sucesso, `header_pack` escreve a word em `out` e retorna `true`.
Se `out` for válido, a falha deve preservar seu valor anterior. Valide a entrada
antes de alterar a saída: descartar os bits que não cabem não é uma forma de
rejeitar um valor inválido.

`header_unpack` recebe
um `Header *` válido e deve fazer decode de qualquer word de 32 bits.
`store_le32` e `load_le32` recebem uma região válida de quatro bytes.
Os argumentos de entrada e saída de cada operação não se sobrepõem.
A conversão deve usar bytes e campos explícitos.

## Antes de começar

### Linguagens e ambiente

A implementação de referência usa **C11**, mas você pode escolher outra linguagem,
como C, Rust, Go ou Python. Rust, Go e Python são alternativas recomendadas.
Use bytes de 8 bits e uma unsigned word de 32 bits. A conversão entre campos,
word e bytes deve ser explícita.

Os materiais fornecem código inicial em C11. Outras linguagens são aceitas com
adaptação do contrato, conforme o guia abaixo.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Você deve conhecer funções, arrays, condições, unsigned integers, hexadecimal e
os operadores bitwise `&`, `|`, `^`, `<<` e `>>`. Instale GCC ou Clang e use um
terminal. O [guia dos materiais](materials/README.md) contém os comandos completos
para compilar, executar os checks e observar a representação do host.

Não aplique as funções que exigem quatro bytes a buffers menores. Null pointers
só são entradas a rejeitar em `header_pack`; as outras funções têm pré-condições.

## Materiais

- [Starter](materials/starter/packet.c): corpos incompletos das quatro funções.
- [Checks públicos](materials/checks/tests.c): test vectors, limites, falhas e round-trip.
- [Fixtures](materials/fixtures/vectors.csv): os quatro test vectors do contrato original.
- [Experimento](materials/experiments/observe.c): word, bytes do host e bytes externos.
- [Guia autocontido](materials/README.md): contrato e instruções de execução.
- [Modelo de relato](report-template.md): roteiro para registrar evidências.

## Etapas da investigação

1. **Prever.** Escolha duas combinações de campos válidos e desenhe as posições
   de bits ocupadas por cada campo. Sem executar código, calcule suas words
   e seus bytes. Para praticar com os test vectors fornecidos, use os campos
   `(version=2, type=17, flags=8, length=4096)` e
   `(version=7, type=31, flags=15, length=1048575)`; registre o raciocínio antes
   de consultar os resultados esperados.
2. **Observar.** Consulte os [test vectors conhecidos](materials/fixtures/vectors.csv).
   Compile o starter e execute os checks. Registre status, primeira falha e contagem.
   A compilação deve funcionar; o starter deve falhar nos testes de funcionalidade.
3. **Explicar.** Justifique a posição de cada campo e a ordem dos quatro bytes.
   Explique por que truncar campos inválidos contraria o contrato e por que a saída
   precisa permanecer intacta em uma falha.
4. **Implementar.** Complete `packet.c`, sem alterar a API, sem usar o layout da
   `struct` como formato externo e sem fornecer payload. Você pode começar pelo
   par `header_pack`/`header_unpack` e depois implementar o par
   `store_le32`/`load_le32`. Crie também seus testes.
5. **Verificar.** Execute os checks e acrescente combinações válidas próprias.
   Rode o experimento e compare host e formato externo. Explique por que dois
   componentes com o mesmo erro podem passar em round-trip, mas falhar nos test vectors.

Um round-trip verifica, por exemplo, se o pack seguido de unpack recupera
os campos originais, ou se escrever e depois ler os bytes recupera a word.
Isso é necessário, mas não basta: se duas funções usarem a mesma ordem errada,
uma poderá desfazer o erro da outra. Os test vectors conhecidos verificam também se
a word e os bytes correspondem exatamente ao formato exigido.

## Critérios de conclusão

Execute também o build com UndefinedBehaviorSanitizer do guia; ele deve terminar com status zero e sem `runtime error`.

Entregue `packet.h`, `packet.c` com as quatro funções implementadas, seus testes
automatizados e um relato curto seguindo o [modelo](report-template.md).
No relato, explique como posicionou e recuperou os campos, por que os bytes têm
aquela ordem e o que os resultados dos testes e do experimento demonstram.
Os checks públicos devem
terminar com status zero e zero falhas após sua implementação. Demonstre:

- os quatro test vectors e seu decoding;
- a rejeição de `version=8`, `type=32`, `flags=16` e `length=1048576`, testados separadamente;
- a preservação do valor de saída `0xA5A5A5A5` em caso de falha;
- a rejeição de null pointers em `header_pack`;
- a conversão de round-trip.

Compare campos individualmente; igualdade dos bytes de uma `struct` não define
igualdade entre headers. Explique a separação entre word e bytes e registre
o ambiente. A execução dos checks complementa a explicação; não prova correção geral.

## Extensões opcionais

Acrescente `uint32_t rotate_left32(uint32_t word, unsigned n)` e
`unsigned count_bits32(uint32_t word)`. A rotação aceita `0 <= n < 32`, incluindo
zero; a contagem retorna o total de bits iguais a um. A tabela completa fica no
[guia dos materiais](materials/README.md). Essas funções são opcionais.

## Participação no clube

Compartilhe uma tentativa com hipótese, comando, entrada e resultado observado.
Ao pedir ajuda, indique o primeiro test vector que falha e a explicação que tentou.
Evite publicar uma solução completa na discussão inicial. Melhorias nos checks
devem citar o requisito do contrato que passam a verificar.

## Referências e atividades relacionadas

Leia as [referências orientadas](references.md) após concluir as etapas obrigatórias: C11 para
regras de shift, Protobuf para leitura com limites e Linux para campos de
rede. A representação binária prepara a leitura de object files, protocolos e
metadados de allocators. A inspiração temática vem do Data Lab de CS:APP;
o formato e a API usados aqui pertencem ao caderno do Oxide Club.
