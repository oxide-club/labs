---
title: Laboratório de Multiplicação Matricial
slug: 008-matrix-lab
summary: Implemente três variantes e investigue tempos e localidade.
question: Por que a mesma operação O(mkn) pode levar tempos diferentes?
draft: false
publishedAt: 2026-10-25
topics: [Matrizes, Localidade, Blocking]
prerequisites: [Arrays em C, Produto matricial, Noções de cache]
tools: [GCC ou Clang, Python 3]
environment: Linux e C11 com double IEEE 754 binary64
difficulty: intermediate
---

## O que vamos investigar

Por que a mesma operação O(mkn) pode levar tempos diferentes?
Implemente C=A×B nas variantes ijk, ikj e blocking. Blocking divide o percurso em
blocos para reutilizar dados. A ordem dos acessos afeta localidade e arredondamento.

### Contrato técnico

Leia o [contrato completo](materials/README.md) antes de editar o starter.
As matrizes são retangulares e contíguas em ordem de linhas. Dimensões: 1..4096;
tile: 1..256; entradas finitas: [-16,16]. As funções sobrescrevem C e preservam A e B.
Erros retornam 1 sem alterar C. A tolerância absoluta é 1e-6 e a relativa é 1e-10.
O contrato fixa pré-condições dos buffers, tamanhos extremos e estado após falhas.

## Antes de começar

### Linguagens e ambiente

Referência: **C11**. Aceitas: Livre sob restrições algorítmicas; por exemplo C, Rust, C++ e Python.
Recomendadas: Rust, C++ e Python. Arrays contíguos row-major binary64; ijk, ikj e blocking próprios; sem BLAS/NumPy no núcleo.
Materiais oficiais: C11 existente.
Equivalência: equivalente sob contrato adaptado.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

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
meta de desempenho. Relacione índices, bytes por double e linhas de cache.

### Implementar e verificar

Implemente ijk, ikj e blocking em matrix.c. Execute `python3 checks/check.py`.
Guarde saída e status. Verifique retangulares, tails, tile maior que dimensões,
erros e chamadas repetidas que sobrescrevem C.

### Medir e interpretar

Siga [o roteiro](experiments/README.md). Valide todas as variantes antes de medir.
Compare conjuntos que caibam e excedam a cache relevante, com tamanhos ajustados ao
hardware. Guarde CSV bruto, warmups, repetições, seed e metadados.
Explique dispersão, vetorização, frequência e carga concorrente. Tempo sozinho não
identifica cache misses nem garante vantagem em outra máquina.

## Critérios de conclusão

Entregue três implementações, checks aprovados, previsão, CSV e relato reproduzível.
Inclua retangulares com tails e dois regimes de capacidade justificados pelo hardware.
Compare mediana e dispersão sem exigir aceleração universal. Explique layout,
reutilização, arredondamento e limitações do experimento.

## Extensões opcionais

Investigue perf counters, SIMD, multithreading ou BLAS. Registre custos de packing e
threads separadamente. Essas extensões não substituem o núcleo.

## Participação no clube

Compartilhe uma tentativa com comando, entrada mínima, saída e pergunta.
Avise quando houver respostas da fixture. Consulte [como participar](/como-participar/)
e mantenha soluções separadas do starter.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md) após o núcleo.
O laboratório de cache introduz localidade; o desafio de precisão numérica aprofunda
arredondamento. Conhecimentos de aprendizado de máquina não são necessários.
