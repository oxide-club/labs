# Implementação histórica opcional

Este guia preserva o contrato anterior como extensão. Seus critérios não encerram
a investigação atual. Consulte o [guia atual](README.md) antes de executar.

# Guia dos materiais — Representação Binária

Este guia pode ser usado dentro do pacote baixado. Os caminhos dos comandos abaixo
partem de `materials/`. Use `cd materials` a partir da raiz do laboratório.
São necessários um compilador C11 (GCC ou Clang), terminal e bytes de oito bits.
`uint8_t` e `uint32_t` devem estar disponíveis. Não há instalação de bibliotecas.

## Contrato

Mantenha exatamente as declarações de `starter/packet.h`. `Header` contém quatro
campos `uint32_t`: `version`, `type`, `flags` e `length`, nessa ordem.

| Campo | Bits da palavra, com bit zero menos significativo | Faixa |
| --- | --- | --- |
| version | 31 a 29 | 0 a 7 |
| type | 28 a 24 | 0 a 31 |
| flags | 23 a 20 | 0 a 15 |
| length | 19 a 0 | 0 a 1048575 |

Todos os valores nessas faixas são válidos. `length` não exige payload.
A representação externa ocupa quatro bytes little-endian, independentemente da
ordem de bytes do host.

- `bool header_pack(const Header *in, uint32_t *out)` retorna `false` se um ponteiro
  for nulo ou um campo estiver fora da faixa. Se `out` for válido, uma falha deve
  preservar seu valor anterior. Em sucesso, escreve a palavra e retorna `true`.
- `void header_unpack(uint32_t word, Header *out)` recebe um ponteiro válido para
  `Header`. Qualquer palavra de 32 bits é decodificável.
- `void store_le32(uint8_t out[4], uint32_t word)` e
  `uint32_t load_le32(const uint8_t in[4])` recebem uma região válida de quatro bytes.
- Os argumentos de entrada e saída de cada operação não se sobrepõem.
- Faça a conversão por bytes e campos explícitos. O layout da `struct` não é o
  formato do arquivo. Não serialize o bloco de memória de `Header`.

## Prever e observar

Desenhe primeiro os campos de dois exemplos. Calcule a palavra em hexadecimal e
os bytes na ordem em que seriam gravados. Depois compare com estes fixtures:

| version | type | flags | length | Palavra | Bytes externos |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 0 | 0 | 0x00000000 | 00 00 00 00 |
| 1 | 2 | 5 | 258 | 0x22500102 | 02 01 50 22 |
| 2 | 17 | 8 | 4096 | 0x51801000 | 00 10 80 51 |
| 7 | 31 | 15 | 1048575 | 0xFFFFFFFF | FF FF FF FF |

`fixtures/vectors.csv` contém esses mesmos quatro vetores, em CC0-1.0.
`checks/tests.c` mantém constantes independentes do código sob teste, para que
encoder e decoder com o mesmo bug não sejam aceitos apenas pela ida e volta.

Compile e execute:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O2 -I starter starter/packet.c checks/tests.c -o /tmp/oxide-packet-tests
/tmp/oxide-packet-tests
```

O starter compila, mas ainda retorna resultados incompletos. A execução inicial
termina com status 1 e falhas: esse é o trabalho a implementar. Os checks mostram
até 20 falhas detalhadas e depois a contagem total. Não modifique os resultados
esperados para obter status zero.

## Explicar e implementar

Implemente as quatro funções em `starter/packet.c`. Antes de escolher uma máscara
ou deslocamento, explique quais bits ele seleciona. Consulte C11 6.5.7 quando
precisar justificar tipo e limite do deslocamento. Valide os campos antes de
alterar a saída. Crie seus próprios `tests.c` e compare campos individualmente.

Os checks fornecidos exercitam vetores diretos de pack/unpack/store/load, todos os
32 bits isoladamente, sentinels nos bytes vizinhos à escrita, oito rejeições
(campos imediatamente fora da faixa e `UINT32_MAX`), preservação da saída,
nulos previstos na API e 32768 combinações válidas. Não chamam as demais funções
com nulos nem buffers menores que quatro bytes: isso violaria pré-condições.

## Verificar e investigar

Após completar as funções, espere `164189 verificacoes; 0 falhas` e status zero.
Para concluir, compile também com UndefinedBehaviorSanitizer e exija status zero sem `runtime error`:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O1 -g -fsanitize=undefined -fno-sanitize-recover=all -I starter starter/packet.c checks/tests.c -o /tmp/oxide-packet-ubsan
/tmp/oxide-packet-ubsan
```

Execute o experimento antes e depois da implementação:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O2 -I starter starter/packet.c experiments/observe.c -o /tmp/oxide-packet-observe
/tmp/oxide-packet-observe
```

A palavra é `0x22500102`. Após implementar, `external` deve mostrar `02 01 50 22`.
Antes disso, o starter deixa o sentinel `A5 A5 A5 A5`. A linha `host` é uma
observação da máquina atual; não a use como definição do formato externo.
`sizeof Header` descreve memória local e pode incluir padding. Não suponha que
esse tamanho seja o tamanho serializado. A leitura via `unsigned char` no
experimento observa bytes do objeto; não implementa a serialização.

Registre a saída, a versão do compilador (`cc --version`), flags e arquitetura.
Responda: a posição numérica dos campos depende da endianness? Por que quatro
vetores independentes ainda são necessários se a ida e volta passa? Que evidência
faltaria para afirmar que o código funciona em outro host? Use o
[modelo de relato](../report-template.md).

## Extensão opcional

As extensões não alteram a API obrigatória. Se as implementar, declare suas
assinaturas separadamente no header e escreva checks próprios:

```c
uint32_t rotate_left32(uint32_t word, unsigned n);
unsigned count_bits32(uint32_t word);
```

A rotação tem pré-condição `0 <= n < 32`; zero deve estar definido. A contagem
retorna o número de bits iguais a um.

| Operação | Esperado |
| --- | --- |
| rotate_left32(0x12345678, 0) | 0x12345678 |
| rotate_left32(0x12345678, 8) | 0x34567812 |
| rotate_left32(0x80000001, 1) | 0x00000003 |
| rotate_left32(0x00000001, 31) | 0x80000000 |
| count_bits32(0) | 0 |
| count_bits32(0x80000001) | 2 |
| count_bits32(0xFFFFFFFF) | 32 |

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** Livre; por exemplo C, Rust, Go e Python.

**Linguagens recomendadas:** Rust, Go e Python.

**Restrições técnicas e plataforma:** Bytes de 8 bits; palavra sem sinal de 32 bits; conversão explícita de campos e bytes.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve os campos de 3/5/4/20 bits, os quatro vetores CSV e little-endian. Rejeite valores fora da faixa antes de shifts: não trunque campos inválidos. Em APIs por valor, use um resultado de sucesso/erro; uma falha não pode alterar o objeto de saída. As pré-condições de ponteiros continuam obrigatórias na API C. Em Python, imponha 0..2^32-1; inteiros arbitrários não ampliam o domínio.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

Na extensão rotate/count, execute os checks próprios também sob UBSan. Inclua `rotate_left32(x, 0)`: deslocar por 32 é comportamento indefinido mesmo quando o valor observado parece correto.

## Licenças

Código original: MIT. Fixtures: CC0-1.0. Documentação: CC BY 4.0.
As leituras em [references.md](../references.md) conservam as licenças de origem.
