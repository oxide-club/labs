---
title: Laboratório de Multiplicação Matricial
area: numerical-computing
slug: 008-matrix-lab
summary: Implemente três variantes e investigue tempos e locality.
question: Por que a mesma operação O(mkn) pode levar tempos diferentes?
draft: false
publishedAt: 2026-10-25
topics: [Matrizes, Locality, Blocking]
prerequisites: [Arrays em C, Produto matricial, Noções de cache]
tools: [GCC ou Clang, Python 3]
environment: Linux e C11 com double IEEE 754 binary64
difficulty: intermediate
---

## O que vamos investigar

### O que você vai construir e comparar

Você vai **implementar três maneiras de calcular o mesmo produto de matrizes**
e medir como a ordem de acesso aos dados afeta o tempo. Complete as variantes
`ijk`, `ikj` e `blocking` em `materials/starter/matrix.c`.

Se A tem forma 2×3 e B tem forma 3×2, C terá forma 2×2. Cada posição C[i,j]
combina a linha i de A com a coluna j de B:

```text
C[i,j] = A[i,0]*B[0,j] + A[i,1]*B[1,j] + A[i,2]*B[2,j]
```

| Variante | O que você muda |
| --- | --- |
| `ijk` | Percorre os índices na ordem i, j, k. |
| `ikj` | Percorre os índices na ordem i, k, j. |
| `blocking` | Divide o percurso em blocos para reutilizar dados próximos. |

Primeiro verifique se as três variantes calculam o resultado dentro da tolerância
exigida. Depois execute o benchmark com dados que caibam e que excedam a cache
relevante. Entregue implementações, checks, CSV bruto e uma comparação de mediana
e dispersão. A conclusão não exige que uma variante seja sempre mais rápida.

### Conceitos para a investigação

Você vai implementar C=A×B nas variantes ijk, ikj e blocking para investigar por
que operações com a mesma complexidade O(mkn) podem levar tempos diferentes.
Blocking divide o percurso em blocos para reutilizar dados. A ordem dos acessos
afeta tanto a locality quanto o arredondamento dos resultados.

#### Contrato técnico

Leia o [contrato completo](materials/README.md) antes de editar o starter.
As matrizes são retangulares e contíguas em row-major order. Cada dimensão vai
de 1 a 4096, e o tamanho do bloco (tile) vai de 1 a 256. Os valores de entrada
devem ser finitos e estar em [-16,16]. As funções sobrescrevem C e preservam A e B.
Erros retornam 1 sem alterar C. A tolerância absoluta é 1e-6 e a relativa é 1e-10.
O contrato fixa pré-condições dos buffers, tamanhos extremos e estado após falhas.

## Antes de começar

### Linguagens e ambiente

A implementação de referência usa **C11**. Você pode escolher outra linguagem,
como Rust, C++ ou Python, que são alternativas recomendadas, desde que preserve
as restrições algorítmicas. Use arrays contíguos em row-major order,
com valores binary64, e implemente as variantes ijk, ikj e blocking. Não use
BLAS ou NumPy para realizar as operações da implementação exigida.

Os materiais fornecem código inicial em C11. Outras linguagens são aceitas com
adaptação do contrato, conforme o guia abaixo.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Conheça arrays, loops, produto matricial e cache. Use Linux, C11 e Python 3.
Siga [os comandos locais](README.md). O starter compila, mas retorna MATRIX_TODO.
Não existe medição válida do starter. Registre CPU, cache, versões e flags.

## Materiais

- [Contrato e materiais](materials/README.md).
- [API](materials/starter/matrix.h) e [starter](materials/starter/matrix.c).
- [Checks públicos](checks/check.py), [casos](checks/check.c) e [referência escalar](checks/oracle.h).
- [Benchmark](experiments/benchmark.c) e [roteiro](experiments/README.md).
- [Modelo de relato](report-template.md) e [referências](references.md).

## Etapas da investigação

### Prever

Calcule a fixture 2×3 por 3×2 à mão antes de consultar o check.
Anote os índices acessados por cada ordem e preveja reutilização de A, B e C.
Guarde a hipótese original.

### Observar e explicar

Leia o oráculo. Explique por que uma referência escalar verifica correção sem fixar uma
meta de desempenho. Relacione índices, bytes por double e cache lines.

### Implementar e verificar

Implemente ijk, ikj e blocking em matrix.c. Execute `python3 checks/check.py`.
Guarde saída e status. Verifique matrizes retangulares, tails, tile maior que as dimensões,
erros e chamadas repetidas que sobrescrevem C.

### Medir e interpretar

Siga [o roteiro](experiments/README.md). Valide todas as variantes antes de medir.
Compare conjuntos que caibam e excedam a cache relevante, com tamanhos ajustados ao
hardware. Guarde CSV bruto, warmups, repetições, seed e metadados.
Explique dispersão, vetorização, frequência e carga concorrente. Tempo sozinho não
identifica cache misses nem garante vantagem em outra máquina.

## Critérios de conclusão

Entregue três implementações, checks aprovados, previsão, CSV e relato reproduzível.
Inclua matrizes retangulares com tails e dois regimes de capacidade justificados pelo hardware.
Compare mediana e dispersão sem exigir aceleração universal. Explique layout,
reutilização, arredondamento e limitações do experimento.

## Extensões opcionais

Investigue perf counters, SIMD, multithreading ou BLAS. Registre custos de packing e
threads separadamente. Essas extensões não substituem as etapas obrigatórias.

## Participação no clube

Compartilhe uma tentativa com comando, entrada mínima, saída e pergunta.
Avise quando houver respostas da fixture. Consulte [como participar](/como-participar/)
e mantenha soluções separadas do starter.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md) após concluir as etapas obrigatórias.
O laboratório de cache introduz locality; o desafio de precisão numérica aprofunda
arredondamento. Conhecimentos de aprendizado de máquina não são necessários.
