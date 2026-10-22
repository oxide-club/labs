---
title: Laboratório de Cache e Localidade
slug: 005-cache-e-localidade
summary: Construa um simulador e reúna rastros, tabelas e uma explicação de como a ordem dos acessos afeta os acertos de uma cache.
question: Como a sequência de endereços muda os acertos de uma cache?
draft: false
publishedAt: 2026-10-21
topics: [Cache, Localidade, Mapeamento direto]
prerequisites: [Operadores bit a bit, Estruturas em C, Leitura de arquivos]
tools: [GCC ou Clang, Python 3]
environment: C11 com uint64_t; terminal Linux como referência
difficulty: intermediate
---

## O que vamos investigar

Como a sequência de endereços muda os acertos de uma cache? Vamos construir um
simulador, prever seus resultados e comparar dois percursos da mesma matriz.
Ao concluir, você terá um programa verificável e evidências para explicar
localidade, conflitos de mapeamento e capacidade.

O modelo tem **quatro linhas de 16 bytes**, mapeamento direto e 64 bytes de dados.
Cada linha guarda uma tag e um indicador de validade. Toda execução começa com
as linhas inválidas e os contadores zerados.

Cada linha de entrada é `L 0xENDERECO`: uma leitura de um byte em um endereço de
64 bits sem sinal, com até 16 dígitos hexadecimais. As entradas fornecidas são
válidas. São números do modelo: **nunca converta os endereços em ponteiros**.

Para um endereço `a`:

- `offset = a & 0xF`;
- `index = (a >> 4) & 0x3`;
- `tag = a >> 6`.

Há um hit quando a linha está válida e sua tag coincide. Caso contrário, conte
um miss e instale a nova tag. Se a linha já estava válida, conte também uma
eviction. Um miss carrega conceitualmente o bloco inteiro, sem armazenar seus
bytes no simulador. Cada acesso é de um byte e não atravessa blocos.

A saída contém uma linha `hits=N misses=N evictions=N`. Exija status zero em
execuções bem-sucedidas. As invariantes são `hits + misses == leituras` e
`evictions <= misses`. Tag zero não significa que uma linha é válida.

## Antes de começar

Você precisa conhecer operadores bit a bit, estruturas e leitura de arquivos em
C. Use GCC ou Clang, biblioteca padrão com `uint64_t` e Python 3 para executar os
checks públicos. Linux é o ambiente de referência; não precisamos medir hardware.

Baixe e extraia o pacote. Na raiz do laboratório, execute:

```sh
cc --version
python3 --version
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/starter/cache.c -o cache
```

O esqueleto compila, mas ainda não simula a cache. Registre versões e opções no
relato. Depois de implementar, use `./cache < materials/inputs/trace-a.txt`.

## Materiais

- [Guia dos materiais](materials/README.md): organização e comandos.
- [Código inicial em C](materials/starter/cache.c): esqueleto a implementar.
- [Trace A](materials/inputs/trace-a.txt): oito acessos para previsão manual.
- [Trace B](materials/inputs/trace-b.txt): dezesseis acessos para conferência.
- [Verificações públicas](checks/check.py): casos conhecidos e limites.
- [Modelo de relato](report-template.md): previsão, evidência e conclusão.

O gerador de percursos de matriz faz parte da sua implementação. Os resultados
de conferência abaixo não substituem sua tabela de previsão.

## Etapas da investigação

### 1. Prever os acessos

Antes de implementar, leia o trace A e preencha uma tabela com endereço, offset,
índice, tag, validade anterior e resultado esperado. Explique quais acessos podem
reaproveitar o bloco carregado por uma leitura anterior.

```text
Endereço | Offset | Índice | Tag | Válida antes? | Hit/miss | Substituição?
```

Guarde essa primeira tabela, inclusive os erros: ela é a previsão do experimento.

### 2. Implementar, observar e verificar

Implemente o simulador em `materials/starter/cache.c` ou em um arquivo seu.
Leia endereços sem perder os bits altos. Execute os traces A e B em processos
separados para que cada execução comece vazia. Registre saída e status.

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/starter/cache.c -o cache
./cache < materials/inputs/trace-a.txt
./cache < materials/inputs/trace-b.txt
python3 checks/check.py ./cache
```

<details>
<summary>Conferir resultados dos traces</summary>

| Trace | Hits | Misses | Evictions |
| --- | ---: | ---: | ---: |
| A | 3 | 5 | 3 |
| B | 4 | 12 | 8 |

No trace A, `0x0F`, `0x4F` e `0x1F` são hits. Os acessos `0x40`, `0x00`
(segunda ocorrência) e `0x50` substituem blocos válidos.

</details>

Compare com a previsão e explique uma divergência, se houver. Ao corrigir o
simulador, registre a causa e repita os checks. Verifique entrada vazia, uma
leitura, duas leituras iguais e endereços próximos do limite de 64 bits.

### 3. Investigar a localidade

Esta etapa faz parte do núcleo. Modele uma matriz de bytes `A[N][N]`, armazenada
por linhas, com endereço sintético inicial zero. Escreva um gerador que emita
somente as leituras da matriz no formato de trace.

- Por linhas: para cada `i`, percorra `j` e emita `N*i+j`.
- Por colunas: para cada `j`, percorra `i` e emita `N*i+j`.

Antes de executar, preveja qual percurso terá mais hits para `N=16` e para `N=8`.
Gere os quatro arquivos, rode cada um em uma execução nova do simulador e guarde
os comandos, traces e contadores. A linguagem do gerador é livre; documente como
executá-lo. Confira que cada trace tem exatamente `N*N` leituras.

<details>
<summary>Conferir resultados de localidade</summary>

| N | Percurso | Hits | Misses | Evictions |
| ---: | --- | ---: | ---: | ---: |
| 16 | Linhas | 240 | 16 | 12 |
| 16 | Colunas | 0 | 256 | 252 |
| 8 | Linhas | 60 | 4 | 0 |
| 8 | Colunas | 60 | 4 | 0 |

</details>

Explique por que a diferença desaparece quando toda a matriz cabe nesta cache.
Escolha dois endereços que disputam uma linha e mostre seus índices e tags.
Esses resultados descrevem o simulador; **não são tempos nem contadores de uma
CPU real**.

### 4. Explicar e consolidar

Relacione suas observações com validade, tag, capacidade e ordem de acesso.
Justifique por que capacidade total, sozinha, não elimina conflitos. Inclua a
previsão original, uma tabela conferida e as verificações após a implementação.

## Critérios de conclusão

- O simulador atende ao contrato e aos traces A/B e casos de limite.
- Cada execução começa vazia; as invariantes dos contadores são respeitadas.
- O gerador produz os quatro percursos de matriz e acompanha a entrega.
- O relato reúne previsão, comandos, ambiente, traces e resultados observados.
- A explicação relaciona resultados a localidade e conflitos e distingue o modelo
  de uma medição de hardware.
- Outra pessoa consegue compilar e reproduzir os experimentos com suas instruções.

Entregue código, gerador, traces e relato. Passar nos checks não substitui a
explicação. Não é necessário concluir as extensões.

## Extensões opcionais

Generalize para `S` conjuntos, `E` vias e blocos de `B` bytes. Exija `S` e `B`
potências de dois e `E` positivo. Valide tamanhos antes de alocar. Use
`bloco=a/B`, `conjunto=(a/B)%S` e `tag=(a/B)/S`.

Implemente LRU atualizando recência em cada acesso. Prefira vias inválidas;
caso todas estejam válidas, substitua a menos recente. Em empate, use a menor via.
Com `S=1`, `E=2`, `B=16`, o trace `0x00, 0x10, 0x00, 0x20, 0x10` deve resultar
em `hits=1 misses=4 evictions=2`. Registre separadamente estas alterações.

## Participação no clube

Compartilhe uma tentativa, mesmo incompleta, com sua previsão e o que observou.
Para perguntar, inclua trace mínimo, saída, comando e dúvida específica. Consulte
[como participar](/como-participar/) para acessar a conversa do clube.

Para propor uma melhoria ou compartilhar uma solução acompanhada de evidências,
siga o [guia de contribuição](https://github.com/oxide-club/labs/blob/main/CONTRIBUTING.md).
Mantenha a solução separada do material inicial e sinalize resultados que revelam
as conferências antes que outra pessoa faça a previsão.

## Referências e atividades relacionadas

- [CS:APP — Lab Assignments](https://csapp.cs.cmu.edu/3e/labs.html): inspiração temática.
- [CS:APP — Cache Lab](https://csapp.cs.cmu.edu/3e/cachelab.pdf): leitura relacionada.
- [Biblioteca do clube](/biblioteca): preparação e aprofundamento.
- [Catálogo de desafios](/desafios/): atividades com contratos delimitados.

O modelo, os traces e o roteiro deste laboratório são autorais do Oxide Club.
