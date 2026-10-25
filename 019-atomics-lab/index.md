---
title: "Laboratório de Atomics e memory ordering"
area: "concurrency-parallelism"
slug: "019-atomics-lab"
summary: "Compare ordenações atômicas com Loom e explique as observações por relações de sincronização."
question: "Por que duas variáveis atômicas podem comunicar um estado logicamente inconsistente?"
draft: false
publishedAt: 2026-10-25
topics: ["Atomics", "Memory ordering", "Concorrência"]
prerequisites: ["Rust", "Threads", "Operações atômicas", "Happens-before"]
tools: ["Cargo", "Loom"]
environment: "Rust 1.98.1, threads e Loom 0.7.2; limites no guia local"
difficulty: advanced
---

## O que vamos investigar

Investigue por que um consumidor pode observar prontidão sem obter o valor que o produtor pretendeu publicar, mesmo quando ambos os campos são atômicos. Use um protocolo com um produtor que registra `42` em `data` e depois anuncia prontidão em `ready`, e um consumidor que faz uma tentativa de leitura, sem esperar indefinidamente.

Antes de executar, preveja os resultados permitidos nas variantes Relaxed, Release/Acquire e SeqCst. Construa o experimento one-shot, examine o contraexemplo da configuração fraca no modelo instrumentado e confronte as previsões com as observações. A explicação deve identificar o caminho de sincronização; “dar tempo para a outra thread” não fundamenta a conclusão.

### Por que investigar este mecanismo

Uma operação atômica protege seu próprio acesso; o protocolo precisa estabelecer como observações de variáveis diferentes se relacionam. `Relaxed`, `Acquire`, `Release` e `SeqCst` oferecem garantias distintas, e essas diferenças não podem ser deduzidas apenas do resultado de uma execução local. [R26.1](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html).

O laboratório usa um dado atômico e uma flag atômica. Assim, a variante incorreta apresenta um erro lógico de publicação sem introduzir um acesso não atômico concorrente. O participante poderá investigar observações permitidas sem executar deliberadamente uma data race.

### Objetivos de aprendizagem

- Separar atomicidade de uma operação, ordem no programa e sincronização entre threads.
- Formular a condição que relaciona a observação de prontidão ao valor publicado e prever quais resultados cada variante permite.
- Explicar quando um load Acquire sincroniza com um store Release.
- Obter e interpretar um contraexemplo no modelo instrumentado, confrontando-o com a previsão registrada.
- Distinguir o resultado previsto, a observação obtida e a explicação baseada em happens-before.
- Delimitar o que um resultado de Loom demonstra e quais propriedades permanecem fora do modelo.

### Conceitos trabalhados

Publicação one-shot; relação reads-from; sincronização release/acquire; observações permitidas; modelo de memória; model checking limitado; instrumentação; diferença entre safety e progresso.

### Contrato técnico

O estado compartilhado contém somente `data: AtomicUsize`, inicialmente `0`, e `ready: AtomicBool`, inicialmente `false`. Há uma publicação, sem reset, e uma tentativa de consumo. O produtor executa primeiro o store de `42` e depois o store de `true`. O consumidor executa `try_read() -> Option<usize>`: se observar `false`, retorna `None`; se observar `true`, lê `data` e retorna `Some(valor)`. O dado continua atômico em todas as variantes.

O modelo tem dois papéis concorrentes: produtor em uma thread criada e consumidor no corpo do teste. `join` ocorre depois de registrar o resultado do consumidor; antecipá-lo introduziria sincronização adicional e mudaria o experimento. Não se usam sleeps, mutexes, canais ou outras flags para forçar a ordem relevante.

| Variante | Acessos a `data` | Store/load de `ready` | Propriedade a investigar |
| --- | --- | --- | --- |
| Fraca | `Relaxed` | `Relaxed` / `Relaxed` | `Some(0)` não é excluído pelo contrato de memória. |
| Publicação | `Relaxed` | `Release` / `Acquire` | Se retornar `Some`, o valor deve ser `42`. |
| Referência forte | `SeqCst` | `SeqCst` / `SeqCst` | A mesma propriedade, com garantias adicionais a identificar. |

`None` é resultado válido em todas as variantes. Não se exige que o consumidor veja a publicação nesta tentativa. Na variante Release/Acquire, a justificativa precisa mencionar que o load de prontidão leu o valor daquele store; os nomes das ordenações, isoladamente, não constituem uma prova.

Todas as operações relevantes precisam usar os tipos instrumentados quando o teste roda com Loom. Passar no modelo não prova todos os comportamentos do programa, nem todos os efeitos possíveis de ordenações relaxadas: há limitações de instrumentação, tamanho do modelo e cobertura do modelo de memória. [R26.2](https://docs.rs/loom/0.7.2/loom/).

## Antes de começar

Rust com `Arc`, `thread::spawn`, `join` e `Atomic*`; noções de data race, mutex e happens-before; habilidade de ler um teste concorrente. A atividade introdutória de concorrência é recomendada. Implementar estruturas lock-free, compare-and-swap loops ou gerenciamento de memória concorrente não é necessário.

### Linguagens e ambiente

Rust 1.98.1, threads e Loom 0.7.2; limites no guia local.

Rust faz parte do mecanismo investigado e é obrigatório no núcleo.

**Aprovado para publicação.** O [guia local](README.md) descreve os materiais, comandos e limites de execução.

## Materiais

Leia o [guia dos materiais](materials/README.md). Use o [modelo de relato](report-template.md) para registrar a investigação. O guia identifica os instrumentos fornecidos e as partes que o participante deve implementar.

O pacote fornece esqueleto `std`/Loom, harness, fixtures sequenciais e limites registrados. A preparação reproduziu o contraexemplo na referência privada com Loom 0.7.2. O participante deve produzir sua própria evidência e distinguir violação da propriedade, erro e interrupção.

## Etapas da investigação

Registre previsões antes de executar. Preserve entradas, comandos e resultados para explicar o mecanismo e os limites de cada conclusão.

### Prever

Registre estas previsões antes das execuções e acrescente o argumento que sustenta cada uma:

- **Publicação fraca:** o protocolo com `ready` em Relaxed não exclui `Some(0)`. Prevê-se que o harness Loom previamente validado pelo clube produza esse contraexemplo; a observação depende da versão, da instrumentação e dos limites registrados, e ainda deve ser obtida pelo participante.
- **Release/Acquire:** quando o load de prontidão lê o `true` escrito pelo store Release da publicação, o resultado esperado é `Some(42)`. `None` continua permitido, pois a tentativa não precisa observar a publicação.
- **SeqCst:** a propriedade “todo `Some` contém `42`” deve continuar satisfeita. Identifique as garantias adicionais a investigar, sem prever que haverá uma diferença visível em toda execução.
- **Execução local e sincronização adicional:** a variante fraca pode não exibir o defeito em execuções com `std`. Antecipar `join` mudaria as relações de sincronização e, portanto, o experimento; não constitui evidência de que Relaxed passou a garantir a publicação.

Uma previsão não é um resultado medido. Registre separadamente o que foi previsto, o que foi observado e o que o modelo de memória permite concluir.

### Conduzir os experimentos

1. Enumere as observações possíveis e registre as hipóteses, separando um resultado antecipado `None` de uma publicação inconsistente `Some(0)`.
2. Desenhe as operações locais, a relação reads-from e a ligação entre o store de prontidão e o load que o observa. Mantenha o `join` depois do registro do resultado.
3. Execute o modelo fraco e identifique o valor observado em cada leitura; não descreva apenas uma ordem de execução de threads. Registre versão, configuração e eventual interrupção por limite.
4. Repita com Release/Acquire e SeqCst, preservando o restante do programa e os limites de exploração. Confronte os resultados com cada previsão.
5. Rode a variante `std` para contraste, sem exigir reprodução do defeito no hardware local. Registre as condições e o alcance dessa observação.
6. Localize como a biblioteca padrão encaminha ordenações aos intrinsics e rejeita combinações inválidas de operação e ordem. [R26.3](https://github.com/rust-lang/rust/blob/1.98.1/library/core/src/sync/atomic.rs).
7. Complete a matriz de evidências e explique o caminho de happens-before, os resultados não observados e os limites da exploração.

### Registrar as evidências

Entregue código das variantes; testes Loom; configuração e versão utilizadas; trace de contraexemplo; tabela de observações; argumento de happens-before; descrição dos limites da exploração. Registre separadamente falha da propriedade, erro de infraestrutura e exploração interrompida. O teste negativo não deve aceitar qualquer panic como confirmação do bug.

Preencha uma matriz que mantenha previsões e observações em campos distintos. Os itens abaixo indicam as evidências a produzir, sem antecipar resultados de execução:

| Condição | Previsão registrada antes da execução | Observação e evidência a registrar | Limite da conclusão |
| --- | --- | --- | --- |
| Modelo fraco | `Some(0)` não é excluído; o harness validado deve expor a violação. | Resultado de cada leitura, trace e diagnóstico da propriedade. | Versão, instrumentação e limites da exploração. |
| Modelo Release/Acquire | `None` ou `Some(42)`, sob o contrato. | Observações exploradas e ligação reads-from que sustenta a publicação. | Ausência de contraexemplo no modelo não substitui a justificativa de sincronização. |
| Modelo SeqCst | A mesma propriedade de valor, com garantias adicionais a explicar. | Observações exploradas e comparação do argumento de ordem. | O experimento não precisa tornar toda garantia adicional visível. |
| Execução com `std` | A falha fraca pode não se manifestar localmente. | Resultados, condições de execução e relação com as previsões. | Frequência observada não caracteriza todos os comportamentos permitidos. |

Anexe a análise de por que mover a leitura para depois de `join` altera a pergunta experimental.

### Explicar e delimitar

Relacione cada conclusão à evidência correspondente e ao argumento de sincronização. Um contraexemplo precisa mostrar as leituras que violam a propriedade; um panic sem essa relação, um erro de infraestrutura ou uma exploração interrompida não o substituem. Na publicação correta, explique que o load Acquire leu o valor daquele store Release e por que essa relação conecta os acessos a `data`.

A ausência de `Some(0)` em uma CPU, em uma campanha com `std` ou em uma exploração incompleta não torna correta a variante fraca. Passar no modelo não prova todos os comportamentos do programa, pois a instrumentação, o tamanho do modelo e sua cobertura de ordenações relaxadas limitam a inferência. Não conclua progresso, fairness, lock-freedom ou wait-freedom a partir desta propriedade de safety. Explique também por que `AcqRel` se aplica a operações que combinam leitura e escrita, e não a um simples load ou store.

## Critérios de conclusão

Sem publicação iniciada, uma tentativa deve produzir `None`. Com publicação concluída antes de começar uma leitura sequencial, a variante correta deve produzir `Some(42)`. No modelo concorrente fraco, a propriedade “todo `Some` contém `42`” deve fornecer o contraexemplo previsto pelo harness validado. Nas variantes corretas, toda observação explorada precisa ser `None` ou `Some(42)`.

Mudar a leitura para depois de `join` deve ser reconhecido como alteração do experimento, e não como correção por ordering. O relatório precisa explicar por que `AcqRel` pertence a operações que combinam leitura e escrita e não será usado como simples load ou store. Nenhuma conclusão exige observar falha em uma CPU específica.

Uma previsão refutada pode ser um resultado válido. Erro de preparação, instrumento incorreto ou timeout não classificado não responde à pergunta experimental. Registre requisitos bloqueados e repita-os em ambiente compatível antes de concluir o núcleo.

## Extensões opcionais

Mais consumidores, republicação, filas SPSC e false sharing exigem novas invariantes. O núcleo não prova lock-freedom, wait-freedom, fairness nem progresso. Benchmarks de ordenações são extensão e não substituem o argumento de correção.

## Participação no clube

Compartilhe código e relato em seu próprio repositório. Apresente a pergunta, a previsão inicial, uma entrada pequena, os comandos e as evidências na conversa do clube. Você pode compartilhar uma tentativa incompleta; identifique o que ainda não foi executado ou explicado.

Use o [modelo de relato](report-template.md). Preserve o limite de páginas indicado nos entregáveis, quando houver; mantenha código, logs e dados extensos em arquivos próprios.

## Referências e atividades relacionadas

As [leituras orientadas](references.md) indicam documentação e código real. Relacione a investigação aos conhecimentos prévios e às atividades citadas, sem tratá-las como uma sequência obrigatória. Os IDs em prosa identificam atividades do catálogo; propostas em elaboração não equivalem a materiais já publicados.
