---
title: Laboratório de Computação Paralela em GPU
area: concurrency-parallelism
slug: 017-gpu-lab
summary: Implemente soma vetorial e reduction em CUDA e separe cálculo de comunicação.
question: Quando a distribuição de trabalho compensa o custo de transferir dados para a GPU?
draft: false
publishedAt: 2026-10-25
topics: [GPU, Paralelismo, Memória, CUDA]
prerequisites: [Arrays, Concorrência, Reductions, Medição]
tools: [CUDA, nvcc, C, Python 3]
environment: Linux com GPU NVIDIA compatível e CUDA Toolkit; preparação CPU sem GPU
difficulty: advanced
---

## O que vamos investigar

Na GPU, cada thread executa uma parte do trabalho. Um bloco agrupa threads que
podem cooperar usando memória compartilhada e barreiras de sincronização (barriers).
Você vai implementar soma vetorial e uma redução (reduction), que combina os
elementos de um vetor em uma soma escalar.
Investigue como limites, acessos à memória global e sincronização afetam essas operações.

### Contrato técnico

O [contrato completo](materials/contract.md) define interfaces e medições.
Implemente somente os mecanismos centrais em `materials/kernels.cu`.
A soma deve produzir `out[i] = a[i] + b[i]`. A reduction deve produzir a soma de `a`, inteiramente na GPU.
Use `long long` de 64 bits e comparação exata, sem tolerância.
As entradas contêm de 0 a 4.194.305 valores em `[-1024,1024]`.
Todos os intermediários da reduction ficam em `[-4294968320,4294968320]`: não há overflow nesse contrato.
Os blocos têm 64, 128, 256 ou 512 threads; é obrigatório testar blocos finais incompletos, com elementos restantes (tail).

## Antes de começar

### Linguagens e ambiente

A referência usa **C na CPU e CUDA C++ na GPU**. São aceitas tecnologias que
executem computação em um dispositivo real, como CUDA C++, HIP C++ e WGSL com Rust;
essas também são as opções recomendadas. Para CUDA, Toolkit, runtime, driver e
GPU devem ser compatíveis.

Os materiais fornecem código C para CPU e código inicial em CUDA C++. A compilação
CUDA, a sondagem do ambiente (probe), os checks GPU e a medição foram executados
em 25/10/2026 na RTX 4060, com nvcc 13.4 e driver 615.78.08. Uma implementação
privada passou nas verificações; o código inicial mantém os TODOs. Consulte o
registro de preparação.

Outras tecnologias são aceitas com adaptação do contrato. A execução em CPU serve
para comparação e preparação; não substitui a execução em GPU.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Leia o [guia local](README.md). Revise arrays, reductions associativas, barriers e concorrência.
Para a preparação CPU, use compilador C11, Make e Python 3.
Para CUDA, use `nvcc`, runtime e GPU compatíveis entre si. Driver e `nvidia-smi` sozinhos não fornecem o compilador.
Registre versões e modelo da GPU. Sem esse ambiente, conclua apenas a preparação CPU e a análise teórica; mantenha as medições pendentes.

## Materiais

O [guia de materiais](materials/README.md) explica os comandos e o starter.
O [verificador](checks/check.py) compara o suporte CPU com aritmética Python independente.
O runner GPU compara cada elemento e a reduction com a referência CPU antes de publicar tempos.
Os [dados](experiments/datasets.csv) definem tamanhos pequeno, médio e grande por geração determinística.
Use o [roteiro de experiências](experiments/README.md) e o [modelo de relato](report-template.md).

## Etapas da investigação

1. **Prever:** desenhe a distribuição de 65 valores em dois blocos de 64 threads. No segundo bloco, identifique a thread com dado e as 63 threads sem dado e preveja o custo relativo das transferências.
2. **Observar:** execute `make -C materials cpu` e `python3 checks/check.py`. Registre a confirmação CPU; ela não representa uma execução GPU.
3. **Explicar:** descreva memória global, compartilhada e local à thread. Explique por que threads de um bloco parcial ainda precisam respeitar barriers coletivas.
4. **Implementar:** escreva soma e reduction em `kernels.cu`. Inclua tails, sincronização e verificações de erros de cada kernel launch. Não use uma biblioteca que resolva a reduction.
5. **Verificar:** compile com `make -C materials gpu`. Execute `python3 checks/check.py --gpu`; o starter deve falhar com operação não suportada. Depois da implementação, todos os casos devem passar.
6. **Medir:** execute o roteiro apenas após correção. Registre 10 amostras por combinação de tamanho e bloco, incluindo tempos de kernel, H2D, D2H e total.
7. **Interpretar:** compare CPU e GPU, explicando o escopo de cada tempo. Identifique uma observação em que comunicação ou kernel launch tenha impacto relevante; não presuma que a GPU vence.

## Critérios de conclusão

Entregue os kernels e os checks GPU aprovados nos tamanhos públicos, incluindo zero e blocos parciais.
Execute `compute-sanitizer --tool memcheck --error-exitcode 1 materials/build/gpu 65 64 3`
e `compute-sanitizer --tool racecheck --error-exitcode 1 materials/build/gpu 513 256 9`.
Ambos devem terminar sem erros nem hazards. O padding do runner não substitui esses diagnósticos.
Explique o mapeamento de índices, a identidade da soma, as barriers e o avanço entre passagens.
Entregue CSV de execuções reais, ambiente, flags e uma interpretação limitada ao hardware usado.
Se não houver CUDA funcional, entregue a referência CPU verificada e a análise, indicando execução GPU pendente.
Essa entrega preparatória não conclui a implementação nem a medição GPU.

## Extensões opcionais

Compare acessos contíguos com acessos espaçados, sem alterar resultados.
Investigue divergência, ocupação e memória compartilhada com um profiler.
Uma variante de ponto flutuante deve definir tolerância e justificar a alteração da ordem das somas.

## Participação no clube

Compartilhe uma hipótese, o comando, a entrada e a evidência no formato do relatório.
Informe se a execução ocorreu em CPU ou GPU. Ao pedir ajuda, inclua o primeiro erro CUDA e o tamanho do bloco.

## Referências e atividades relacionadas

Consulte as [leituras orientadas](references.md) depois de concluir a implementação exigida.
Relacione as observações com multiplicação matricial, localidade e sincronização.
