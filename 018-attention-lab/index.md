---
title: Laboratório de Mecanismos de Atenção
area: numerical-computing
slug: 018-attention-lab
summary: Implemente attention com aritmética explícita e investigue estabilidade, causalidade e memória.
question: Como comparar posições de uma sequência sem perder estabilidade numérica nem consultar posições futuras?
draft: false
publishedAt: 2026-10-25
topics: [Álgebra linear, Attention, Ponto flutuante, Memória]
prerequisites: [Matrizes, Transposição, Produtos matriciais, Exponenciação, Python]
tools: [Python 3, Biblioteca padrão]
environment: Python 3.10 ou posterior com float binary64; referência Linux e CPython
difficulty: advanced
---

## O que vamos investigar

Scaled dot-product attention compara consultas Q com chaves K e usa os pesos
resultantes para combinar valores V. Um score mede a relação entre duas posições.
O softmax transforma uma linha de scores em probabilidades que somam 1.
A causal mask proíbe que uma posição use valores de posições futuras.
Investigue `Attention(Q,K,V) = softmax(Q × Kᵀ / sqrt(d_k) + M) × V`.
Não é necessário construir um LLM para observar esse mecanismo.

### Contrato técnico

O [contrato completo](materials/contract.md) define três funções: `scaled_scores`,
`softmax` e `attention`. Use listas Python e aritmética explícita, sem framework
ou autograd. Q/K têm forma N × d_k; V tem N × d_v. Os limites inclusivos são
`1 ≤ N ≤ 256` e `1 ≤ d_k,d_v ≤ 64`. Elementos de Q/K/V são números nativos
finitos com módulo até `1e6`, exceto booleanos.

Valide entradas e preserve-as no sucesso e na falha. Entradas inválidas levantam
`ValueError`. `attention` devolve scores antes da causal mask, probabilidades e saída.
`softmax` subtrai o máximo antes de exponenciar. Na causal mask, `j > i`
recebe `-inf` antes do softmax e probabilidade exatamente zero depois dele.
O softmax isolado rejeita linhas totalmente mascaradas; a diagonal causal
permitida impede esse caso em attention. Use tolerância relativa `1e-9` e
absoluta `1e-12`, com zeros mascarados exatos e soma de probabilidades a `1e-12` de 1.

## Antes de começar

### Linguagens e ambiente

Referência: **Python**. Aceitas: Livre; por exemplo C, Rust, C++ e Python.
Recomendadas: Rust, C++ e Python. Binary64; produtos, transposição, softmax estável e causal mask próprios; sem framework central.
Materiais oficiais: Python existente.
Equivalência: equivalente sob contrato adaptado.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

Revise vetores, produto matricial, transposição e exponenciação.
O [guia local](README.md) mostra os comandos a executar na raiz do laboratório.
Use Python 3.10 ou posterior, sem dependências externas. Registre versão,
implementação Python, sistema e características de `float`.
Multiplicação matricial e representação de números são conhecimentos prévios
recomendados. Não se exige experiência com treinamento de modelos.

## Materiais

O [guia de materiais](materials/README.md) organiza o starter e os comandos.
As [entradas e respostas conhecidas](materials/fixtures/cases.json) incluem
scores, probabilidades e saídas. Leia a [derivação dos fixtures](materials/fixtures/README.md).
O [check público](checks/check.py) verifica o contrato do participante;
a [conferência de fixtures](checks/verify_fixtures.py) verifica os dados sem usar o starter.
O [roteiro experimental](experiments/README.md) separa previsão de memória e
observação da implementação. Registre evidências no [modelo de relato](report-template.md).

## Etapas da investigação

1. **Prever:** calcule à mão os quatro scores do caso `scaled-asymmetric`.
   Desenhe a causal mask 2 × 2 e preveja a primeira saída com e sem causal mask.
   Calcule também os scores de `irrational-scale` e explique por que truncar
   sqrt(2) altera os pesos e a saída.
   Compare sua tabela com os fixtures somente depois de registrar a previsão.
2. **Observar:** execute `python3 checks/verify_fixtures.py` e
   `python3 checks/check.py`. Registre a conferência dos dados e a falha
   `NotImplementedError` do starter. Não interprete essa falha como defeito no pacote.
3. **Explicar:** descreva por que subtrair o máximo preserva as razões entre
   exponenciais e evita overflow em `[1000,1001]`. Explique por que uma linha
   de `-inf` requer a política explícita do contrato.
4. **Implementar:** complete `materials/attention.py`, incluindo validação,
   transposição, produtos, escala, causal mask e softmax estável. Mantenha os
   intermediários observáveis e não delegue essas operações a bibliotecas prontas.
5. **Verificar:** execute `python3 checks/check.py`. Entregue a saída dos checks
   e explique o teste que modifica posições futuras sem alterar o prefixo causal.
   Confira também limites, entradas inválidas e preservação das entradas.
6. **Medir:** depois da correção, execute os dois modos de
   `experiments/memory.py` conforme o roteiro. Registre as três repetições por N.
7. **Interpretar:** compare N e 2N. O número de scores quadruplica; investigue
   por que memória rastreada e tempo não precisam seguir exatamente essa razão.
   Distinga dados densos binary64, objetos Python e pico de allocations da chamada.

## Critérios de conclusão

Entregue implementação própria, checks aprovados e tabelas de intermediários.
Explique escala, estabilidade, causal mask e política de linha totalmente mascarada.
Inclua CSV teórico e medições reais para comprimentos crescentes, ambiente e
repetições. A análise deve relacionar a matriz explícita N × N ao custo quadrático
sem apresentar estimativas como medições. Os checks públicos não demonstram
correção geral: justifique também os invariantes e as limitações da sua solução.

## Extensões opcionais

Explore multi-head, projeções Q/K/V, KV cache ou tiling para evitar materializar
as duas matrizes inteiras. Declare a alteração de contrato e compare resultados
antes de comparar recursos. Treinamento e backpropagation ficam fora do núcleo.

## Participação no clube

Compartilhe a hipótese inicial, uma entrada pequena, o comando e a primeira
diferença observada. Use o modelo de relato para distinguir resultados normativos,
observações e pontos ainda não verificados. Não compartilhe apenas um tempo agregado.

## Referências e atividades relacionadas

As [leituras orientadas](references.md) conectam as operações a um forward pass
real depois do núcleo. Relacione o laboratório a multiplicação matricial,
representação de números e à nota sobre memória de LLMs.
