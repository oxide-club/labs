# Análise do caráter investigativo dos laboratórios

Considero **001 — Representação Binária, 004 — Alocação de Memória e 009 — Máquinas Virtuais os candidatos mais fortes a desafios apresentados como laboratórios**. Nos três, implementar corretamente um contrato domina a atividade; a investigação acrescenta sobretudo previsões de resultados, traces e justificativas da implementação.

**003 — Segurança de Memória tem investigação substantiva, mas forte redundância pedagógica com o desafio 016.** O laboratório 002 também compartilha o método do desafio 015, embora tenha uma entrega investigativa mais claramente distinta. Os laboratórios 006 e 015 merecem revisão por seu predomínio de implementação, mas possuem perguntas causais reais. Não os equiparo aos três primeiros.

Não encontrei laboratório literalmente desprovido de qualquer observação ou explicação. O problema é a **insuficiência ou subordinação da investigação**, e não a ausência das palavras “hipótese”, “experimento” ou “relato”.

## Escopo e critérios

Foram lidos os enunciados dos 18 laboratórios e dos 21 desafios, com consulta aos roteiros experimentais e materiais relevantes para distinguir investigação de verificação de implementação. Esta é uma análise editorial e curricular, não uma auditoria de correção dos programas; os experimentos não foram executados.

Base de labs: `cce149cc4639807252b282f4a05d43706abf2299`, branch de origem `main`. Base de challenges: `a8ac590c7cd6d85da9d0ae832fa226f67a2f109b`, branch `feat/roadmap-challenges`. A análise foi realizada em worktree isolada, na branch `codex/labs-investigative-audit`. A pasta não rastreada `.worktrees/` de challenges não integra o catálogo comparado.

Usei quatro perguntas para avaliar cada núcleo obrigatório:

1. Há uma pergunta sobre o funcionamento e a causa do comportamento, além de “como implementar esta API”?
2. O participante precisa formular uma previsão ou interpretação que será confrontada com evidência?
3. O procedimento permite observar ou variar algo relevante ao mecanismo, além de verificar saídas corretas?
4. A conclusão exige uma explicação sustentada por evidências que acrescente compreensão à solução funcional?

Uma investigação pode ser guiada, determinística, qualitativa ou baseada em simulação. Não precisa gerar resultados inéditos, usar hardware real ou incluir benchmark. Também não perde seu caráter por exigir código complexo. Por outro lado, escrever um diagrama ou explicar invariantes não transforma automaticamente um desafio em laboratório: vários desafios já exigem isso.

As extensões opcionais e leituras complementares foram consideradas, mas não usadas para suprir uma lacuna do percurso obrigatório. “Sobreposição” abaixo significa repetição de trabalho ou de objetivos de aprendizagem; não afirma cópia textual ou equivalência integral de APIs.

## Casos com estrutura predominante de desafio

### 001 Representação Binária

**Parecer: desafio de implementação com demonstração complementar. Confiança alta.**

O produto central é um encoder/decoder de quatro funções. O enunciado fixa posições, larguras, intervalos, ordem dos bytes e política de falha. As previsões consistem em calcular duas instâncias desse formato; a validação exige vetores, rejeições, preservação de saída e round-trip. Isso é uma estrutura típica de problema com contrato e testes. Veja [as funções e o formato](../001-binary-lab/index.md#as-quatro-funções-que-você-deve-implementar) e [os critérios](../001-binary-lab/index.md#critérios-de-conclusão).

Há uma observação legítima: [observe.c](../001-binary-lab/materials/experiments/observe.c) imprime bytes do host, bytes externos e tamanhos. O roteiro também exige explicar erros simétricos no round-trip. Esses elementos impedem dizer “não há investigação alguma”. Entretanto, a comparação usa uma word fixa, e o percurso não exige aprofundar uma hipótese sobre layout ou representação por meio de casos discriminantes. A maior parte das explicações justifica regras já estabelecidas para a solução.

Há sobreposição parcial com [005 — Base64](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/005-base64/index.md), em manipulação de bits e codificação/decodificação, e [013 — Inspetor de registros](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/013-record-inspector/index.md), em representação externa, endianness e validação. Nenhum deles é uma duplicata exata do header compactado. O principal problema deste laboratório é a modalidade, não a duplicação.

**Decisão sugerida:** classificá-lo como desafio no formato atual, ou exigir um núcleo investigativo mais substantivo antes de mantê-lo em labs.

### 004 Alocação de Memória

**Parecer: desafio e maior redundância funcional do catálogo. Confiança alta.**

O trabalho consiste em implementar `arena_init`, `arena_alloc`, `arena_reset` e `arena_destroy`, respeitando alignment, capacidade, overflow, não sobreposição e preservação de estado. O [roteiro obrigatório](../004-arena-lab/index.md#etapas-da-investigação) pede prever offsets, desenhar padding, implementar e passar nos checks. O experimento [layout.c](../004-arena-lab/materials/experiments/layout.c) apenas consulta tamanhos, alignment e o alinhamento da base de malloc. É uma observação útil, mas pequena diante da implementação exigida.

O [desafio 017 — Arena de memória alinhada](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/017-arena/index.md) já exige o mesmo algoritmo central, invariantes, proteção contra overflow, reset e um diagrama das alocações. Logo, diagrama e justificativa não constituem aqui um diferencial investigativo.

As APIs não são idênticas: no desafio, a região pertence ao chamador e os alignments aceitos vão até 16; no laboratório, a arena obtém a região via malloc, admite alignments até `_Alignof(max_align_t)` e inclui destruição. São diferenças de contrato, mas não uma nova questão experimental.

A extensão de pool repete first-fit, split, coalescing e fragmentação do [desafio 018 — Alocador com liberação individual](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/018-free-list/index.md). Também há diferença: o laboratório conta metadados na capacidade, enquanto o desafio os mantém fora dela. Além de não ser duplicata literal, essa extensão é opcional e não resolve a fragilidade do núcleo.

**Decisão sugerida:** consolidar o núcleo com o desafio 017. A existência de mais funções e de uma extensão de allocator não justifica, por si, um laboratório separado.

### 009 Máquinas Virtuais

**Parecer: desafio de interpretador com trace didático. Confiança alta quanto à sobreposição; moderada a alta quanto à reclassificação.**

O [contrato](../009-vm-lab/index.md#contrato-técnico) define ISA, estado inicial, validação, limites, atomicidade de falhas e formato exato do resultado. O [entregável](../009-vm-lab/index.md#critérios-de-conclusão) reúne implementação, programas válidos/inválidos e trace explicado.

Existe uma intervenção experimental: o [roteiro de trace](../009-vm-lab/experiments/trace.md) manda alterar `JMP 2` para `JMP 8` e explicar o esgotamento do budget. Portanto, não é correto descrevê-lo como totalmente não experimental. Ainda assim, seu alcance fica próximo de um caso de teste da semântica que o participante acabou de implementar.

O [desafio 021 — Uma VM de bytecode](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/021-bytecode/index.md) já exige VM de pilha, aritmética, memória, saltos, validação integral inclusive de código inalcançável, orçamento de instruções e trace do laço. A própria investigação da evolução do PC já faz parte desse desafio.

Existem diferenças reais: a VM do laboratório usa texto, índices de instruções, pilha de 32 elementos, oito variáveis e devolve estados/traces; a do desafio usa bytecode, offsets em bytes, pilha de 64 elementos, 16 posições de memória e outra regra para HALT. São variantes do mesmo núcleo de aprendizagem. Os desafios [019 — RPN](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/019-rpn/index.md) e [020 — Expressões](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/020-expressions/index.md) compartilham partes do tema, mas a correspondência principal é com 021.

**Decisão sugerida:** tratá-lo como variante ou progressão do desafio 021. Para justificar um laboratório separado, a investigação precisa ir além de implementar e rastrear a ISA especificada.

## Investigação existente com redundância relevante

### 003 Segurança de Memória

**Parecer: investigação real, com forte repetição do desafio 016.**

O laboratório exige prever owner/view, capturar um diagnóstico original, ligar alocação/dealocação/acesso e explicar por que uma saída aparentemente correta não legitima um acesso inválido. Isso constitui investigação causal. A [sequência obrigatória](../003-memory-safety-lab/index.md#etapas-da-investigação) não se resume a obter `Club` na saída.

Entretanto, o [desafio 016 — Quem liberou este buffer?](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/016-use-after-free/index.md) já exige ASan, reconstrução da linha do tempo, atribuição de ownership, patch e regressão. Repetem-se mecanismo, ferramenta, evidências e grande parte da explicação exigida.

A distinção técnica é entre uma view interior de string, no laboratório, e uma cópia independente devolvida ao chamador, no desafio. O laboratório também acrescenta uma CLI de offsets; essa parte é predominantemente um novo problema de implementação e validação, não uma investigação adicional equivalente.

**Decisão sugerida:** revisar sua função no currículo antes de manter os dois percursos completos. Eu não o removeria por ausência de investigação; o motivo seria redundância e diferenciação insuficiente.

### 002 Engenharia Reversa

**Parecer: laboratório legítimo, com sobreposição metodológica ao desafio 015.**

O alvo já está pronto. A [entrega central](../002-reverse-engineering-lab/index.md#critérios-de-conclusão) é uma reconstrução explicada: restrições ligadas ao disassembly, entrada aceita, entrada quase correta e comparação responsável pela rejeição. Encontrar a chave, isoladamente, não basta. Isso sustenta sua classificação como laboratório.

O [desafio 015 — O que este executável faz?](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/015-mystery-program/index.md) também exige hipóteses, consultas a executável, pseudocódigo, evidências e validação com entradas novas. A diferença é que seu produto inclui um programa equivalente de transformação de bytes; no laboratório, pseudocódigo é aceito e a ligação de cada restrição às instruções é obrigatória. No desafio, documentar cada correspondência com assembly aparece como extensão.

O [desafio 014 — Que arquivo é este?](https://github.com/oxide-club/challenges/blob/a8ac590c7cd6d85da9d0ae832fa226f67a2f109b/014-mystery-image/index.md) compartilha o método de inferência, mas investiga um formato de dados, não o fluxo de controle do executável. É afinidade metodológica, não duplicação direta.

**Decisão sugerida:** manter 002 como laboratório, deixando explícito seu diferencial. A comparação `-O0`/`-O2` é opcional; não deve ser contabilizada como diferencial obrigatório já existente.

## Casos limítrofes e risco de virar apenas implementação

| Laboratório | Evidência investigativa existente | Fragilidade e parecer |
| --- | --- | --- |
| [006 — Processos e Pipes](../006-processes-lab/index.md#etapas-da-investigação) | Tabela de descritores, EOF, status, reaping e explicações sobre bloqueio do produtor e escritores herdados. | A tarefa central é construir `oxrun`; o [roteiro](../006-processes-lab/materials/experiments/descriptors.md) executa principalmente casos de conformidade após a implementação. Observar com strace é condicional, e não se exige provocar/controlar os mecanismos de bloqueio discutidos. **Híbrido com investigação pouco desenvolvida; revisão prioritária.** Não é duplicata de `wc`: usá-lo no pipeline é usar uma ferramenta. |
| [015 — Execução Assíncrona](../015-async-lab/index.md#etapas-da-investigação) | Trace de poll/wake, distinção Idle/Complete, notificação por outra thread e diagnóstico de espera sem spin. | Executor e evento têm contrato detalhado; o [trace](../015-async-lab/experiments/README.md) usa uma ordem controlada e serve em boa parte para conferir a política exigida. Ainda assim, o [check Linux](../015-async-lab/checks/public.rs) observa CPU e trocas voluntárias de contexto, e o roteiro exige justificar a espera. **Híbrido, com conteúdo investigativo mínimo defensável; não o classificaria como “sem experimentação”.** Não há equivalente direto entre os 21 desafios. |
| [011 — Protocolos Binários](../011-protocol-lab/index.md#etapas-da-investigação) | O mesmo fluxo é submetido a fragmentações diferentes, concatenação e truncamento; exige explicar mensagens disponíveis, estado persistente e EOF. | O [roteiro](../011-protocol-lab/experiments/fragmentation.md) contém resultados normativos e muito trabalho de parser, mas varia uma condição relevante mantendo os bytes. **Manter como laboratório guiado, com risco de reduzir o relato a uma tabela de testes.** Compartilha parsing com 013 e estado entre blocos com 006 de challenges, mas framing incremental tem objeto próprio. Não exige sockets, o que não invalida o experimento em memória. |

Os três casos não têm o mesmo grau de fragilidade: 006 concentra sua explicação causal em perguntas pouco acompanhadas de intervenção; 015 acrescenta observação operacional da espera; 011 possui uma comparação explícita entre fragmentações. Um contrato longo, isoladamente, não fundamenta reclassificação.

## Laboratórios com núcleo investigativo suficientemente distinto

| Laboratório | Investigação obrigatória que justifica mantê-lo |
| --- | --- |
| [005 — Cache e Localidade](../005-cache-lab/index.md#etapas-da-investigação) | Compara percursos por linhas/colunas para N=8 e N=16, exige quatro traces e explica a interação entre capacidade, mapeamento e ordem de acesso. O simulador é instrumento da investigação. |
| [007 — Compilação e Execução](../007-compilation-lab/index.md#etapas-da-investigação) | Inspeciona artefatos, símbolos, relocations, maps e syscalls; provoca erros de linking e compara artefatos após uma alteração. Os programas iniciais já estão completos. |
| [008 — Multiplicação Matricial](../008-matrix-lab/index.md#etapas-da-investigação) | Compara variantes corretas, regimes de capacidade, tiles, mediana e dispersão. O resultado investigativo não depende de uma variante vencer universalmente. |
| [010 — Concorrência e Sincronização](../010-concurrency-lab/index.md#etapas-da-investigação) | Examina interleavings, distingue modelo de UB, compara sincronização e estabelece um ciclo de deadlock controlado. A fila extensa não elimina essa investigação. |
| [012 — ABI e Calling Conventions](../012-abi-lab/index.md#etapas-da-investigação) | Observa passagem de diferentes quantidades de argumentos, stack e registradores, captura argumentos e compara compilações. O assembly é confrontado com o mecanismo observado. |
| [013 — Syscalls](../013-syscalls-lab/index.md#etapas-da-investigação) | Compara interfaces libc/syscall, traces reais de sucesso/EBADF e disassembly. Distingue retornos simulados dos checks de observação real e explica a fronteira usuário/kernel. |
| [014 — Bibliotecas Compartilhadas](../014-dynamic-linking-lab/index.md#etapas-da-investigação) | Compara archive/shared/carregamento explícito, observa dependências e provoca falhas de biblioteca/símbolo, investigando NOW/LAZY. |
| [016 — Isolamento de Processos](../016-isolation-lab/index.md#etapas-da-investigação) | Distingue supervisão, limites e isolamento, exige evidências de processos/recursos e matriz de mecanismos. Algumas experiências dependem de permissões; a alternativa teórica é identificada como tal e não comprova conclusão prática. |
| [017 — Computação Paralela em GPU](../017-gpu-lab/index.md#etapas-da-investigação) | Varia tamanhos/blocos, separa transferências, kernel e total, compara CPU/GPU e interpreta dados reais. Preparação CPU não substitui medição GPU. |
| [018 — Mecanismos de Atenção](../018-attention-lab/index.md#etapas-da-investigação) | Relaciona estabilidade e causalidade a intermediários e compara memória teórica/medida ao variar N, distinguindo modelo denso de objetos Python. |

Não identifiquei nesses dez um desafio do catálogo atual que replique seu núcleo obrigatório. Há relações temáticas e pré-requisitos, especialmente bits, arrays, memória e processamento de dados. Isso não equivale a repetição da atividade.

## Síntese das sobreposições

| Laboratório | Desafio relacionado | Natureza da repetição |
| --- | --- | --- |
| 004 Arena | 017 Arena | **Muito alta:** mesmo algoritmo central, invariantes, reset e diagrama; diferenças de ownership e API. |
| Extensão de 004 | 018 Free-list | **Alta, mas opcional:** first-fit, split, coalescing e fragmentação; metadados e alignment diferentes. |
| 009 VM | 021 Bytecode | **Muito alta:** construção de VM, validação, estado, saltos, budget e trace; ISA e representação diferentes. |
| 003 Segurança de Memória | 016 Use-after-free | **Alta:** diagnóstico, ASan, linha do tempo, ownership e correção; view e cópia independente diferenciam os alvos. |
| 002 Engenharia Reversa | 015 Executável desconhecido | **Moderada:** método e ferramentas próximos, mas predicados ligados ao assembly diferem de implementar transformação equivalente. |
| 001 Representação Binária | 005 Base64 e 013 Inspetor | **Parcial:** bits, conversão e formato externo; nenhum contrato idêntico. |
| 011 Protocolos | 013 Inspetor e 006 Busca em stream | **Parcial:** parsing, limites e estado entre leituras; mecanismo de framing distinto. |

## Prioridade editorial

Eu começaria por **004 e 009**, pois combinam predomínio de desafio com redundância direta. Em seguida, revisaria a modalidade de **001** e a necessidade de manter **003** separado do desafio 016. **006 e 015** precisam de revisão da força das evidências exigidas. **002 e 011** podem permanecer como laboratórios, preservando seus diferenciais investigativos.

Há também uma inconsistência entre os catálogos que afeta essa decisão: os desafios 007, 014, 015 e 016 já exigem investigação, e o 021 já exige trace de execução. Assim, adicionar “prever, observar e explicar” ao mesmo trabalho não estabelece uma distinção curricular suficiente. O diferencial precisa estar na pergunta investigada, no procedimento e no que a evidência permite explicar.

Este relatório não altera enunciados, IDs ou classificação publicada.
