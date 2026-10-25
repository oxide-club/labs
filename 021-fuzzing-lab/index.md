---
title: "Laboratório de Fuzzing e análise de falhas"
area: "data-protocols"
slug: "021-fuzzing-lab"
summary: "Investigue dois defeitos de um parser OXF1 por fuzzing, reprodução, minimização e regressão."
question: "Como transformar entradas inesperadas em defeitos compreendidos e regressões permanentes?"
draft: true
topics: ["Fuzzing", "Parsing binário", "Análise de falhas"]
prerequisites: ["Parsing binário", "Testes", "Diagnóstico de falhas"]
tools: ["libFuzzer ou cargo-fuzz", "ASan e UBSan na variante C"]
environment: "Linux x86-64; C com libFuzzer ou Rust com cargo-fuzz; uma variante para avaliação"
difficulty: advanced
---

## O que vamos investigar

Investigue como entradas inesperadas expõem violações do contrato de um parser e como distinguir descoberta, diagnóstico e correção. O objeto de estudo será um parser isolado de OXF1 preparado pelo clube, com dois defeitos intencionais na variante escolhida. Implemente seu fuzz target como instrumento de investigação, execute a campanha com orçamento fixo e confronte os resultados com um oráculo independente.

Reproduza os dois defeitos fora do motor, minimize pelo menos um caso preservando a identidade do defeito e corrija suas causas. Explique a invariante violada, a relação entre entrada e sintoma e por que a correção atende ao contrato, inclusive para entradas vizinhas.

A descoberta espontânea não é condição de sucesso. Para defeitos não encontrados, use os reproducers do [kit público de apoio](materials/after-campaign/README.md), recomendado para consulta após registrar a campanha. A avaliação exige investigação, correção e regressão dos dois defeitos, identificando quais entradas vieram da campanha e quais foram fornecidas. Corrigir o código integra o experimento: é necessário mostrar como a mudança altera o comportamento que sustentava o diagnóstico.

### Por que investigar este mecanismo

Um crash inicia a investigação: ainda é preciso distinguir rejeição legítima, panic, acesso inválido, erro lógico e esgotamento de recursos. Uma correção deve explicar a violação, atender a entradas vizinhas e permanecer verificável.

libFuzzer executa o target repetidamente no mesmo processo e orienta mutações por cobertura. Recomenda tolerância a entradas arbitrárias, determinismo e controle de recursos ([libFuzzer](https://llvm.org/docs/LibFuzzer.html)).

### Objetivos de aprendizagem

- Formular previsões sobre aceitação, rejeição e falhas a partir do contrato OXF1.
- Construir um harness sem efeitos externos para bytes arbitrários.
- Explicar a contribuição de cada seed e registrar limites da campanha.
- Reproduzir falhas fora do motor de fuzzing.
- Minimizar ao menos um reproducer preservando a mesma classe de defeito.
- Corrigir violações do contrato e acrescentar testes independentes.
- Relatar ausência de descobertas sem concluir que o programa está correto.

### Conceitos trabalhados

Harnesses, corpus, cobertura, oráculos, minimização, triagem e regressão. Um resultado incorreto pode não produzir diagnóstico de sanitizer. As variantes compartilham o formato, mas possuem defeitos próprios.

### Contrato técnico

OXF1 é um formato **criado para este laboratório**, sem finalidade executável. Todos os inteiros multibyte são unsigned little-endian.

| Região | Contrato |
|---|---|
| Bytes 0–3 | Magic ASCII `OXF1`. |
| Byte 4 | Flags: somente bit 0 é permitido; ele indica checksum final. |
| Byte 5 | Número de registros, entre 0 e 16. |
| Bytes 6–7 | Comprimento do payload, entre 0 e 256 bytes. |
| Payload | Exatamente a quantidade declarada de registros. Cada registro contém `type:u8`, `len:u8` e `len` bytes de dados. |
| Tipo 1 | `len = 2`; valor numérico `u16`. |
| Tipo 2 | `len` entre 0 e 32; todos os bytes entre `0x20` e `0x7e`, inclusive. |
| Checksum | Quando indicado, `u16` após o payload: soma dos bytes do payload módulo `65536`. |
| Término | Nenhum byte extra; os registros devem consumir exatamente o payload. |

Entrada maior que 4096 bytes recebe `TooLarge`; o maior documento válido tem 266 bytes. O parser recebe buffer e comprimento e retorna documento ou erro, sem encerrar o processo. Em C, ponteiro nulo é admitido apenas com comprimento zero. A saída contém registros na ordem original, presença de checksum e soma dos valores de tipo 1 em `u32`.

Os erros distinguem `TooLarge`, `Truncated`, `BadMagic`, `BadFlags`, `BadCount`, `BadPayloadLength`, `UnknownType`, `BadRecordLength`, `BadText`, `BadChecksum` e `TrailingData`. Testes com uma violação isolada exigem seu erro específico. Quando coexistirem violações, qualquer erro aplicável é aceito, sem prometer precedência global.

O target não acessa rede, arquivos, relógio ou processos e não executa comandos. O motor pode ler corpus e escrever artefatos em seu diretório; isso não é efeito do parser. Cada chamada libera seus recursos e não deixa estado que altere a seguinte. Rejeição por `Result` ou código de erro é resultado normal. Panic, diagnóstico de sanitizer ou divergência do oráculo identifica falha.

A campanha usa um worker, no máximo 600 segundos ou um milhão de execuções, o que ocorrer primeiro; entrada máxima de 4096 bytes, timeout de dois segundos por caso e limite de RSS de 512 MiB. Registre seed, versões e opções reais. Interrupção por defeito permite reiniciar após preservar o artefato, respeitando o orçamento total. Os mecanismos de limite e minimização são documentados pelo [libFuzzer](https://llvm.org/docs/LibFuzzer.html).

## Antes de começar

Arrays de bytes, parsing, testes, build e leitura de stack traces. Em C, limites de buffers e sanitizers; em Rust, `Result::Err`, panic e configuração de build. Experiência com segurança de memória e protocolos binários é recomendada.

### Linguagens e ambiente

Linux x86-64; C com libFuzzer ou Rust com cargo-fuzz; uma variante para avaliação.

Escolha uma variante: C com libFuzzer ou Rust com cargo-fuzz. As duas preservam OXF1, mas exigem defeitos e diagnósticos próprios. Não é necessário concluir ambas.

**Em elaboração.** A variante C possui materiais executáveis e comandos validados. O piloto permanece pendente; `draft: true` está preservado. O [guia local](README.md) registra ambiente, resultados e limitações.

## Materiais

Leia o [inventário dos materiais](materials/README.md). Use o [modelo de relato](report-template.md) para registrar a investigação. O pacote fornece parser C, corpus, runner determinístico, check de preparação independente e supervisor de campanha. O oráculo completo e os reproducers estão no kit público de apoio, recomendado para consulta após o registro da campanha. O fuzz target permanece incompleto para construção pelo participante.

A variante C contém um defeito de acesso à memória e um erro lógico. O kit público inclui dois reproducers de reserva, sintomas e regressões para conferir a correção. A consulta posterior à campanha é uma orientação pedagógica, sem restrição de acesso. Registre qualquer consulta antecipada e a origem das entradas utilizadas. A variante Rust permanece aceita, sem materiais executáveis preparados nesta revisão.

## Etapas da investigação

Registre previsões antes de executar. Preserve entradas, comandos e resultados para explicar o mecanismo e os limites de cada conclusão.

### Prever

Registre as previsões antes de executar a campanha e antes de aplicar cada correção. Para cada hipótese, indique entrada ou classe de entradas, observação esperada e evidência que a confirmaria ou exigiria sua revisão.

| Hipótese verificável | Previsão e verificação |
|---|---|
| O contrato distingue rejeição normal de defeito. | Casos válidos produzem o documento calculado independentemente; casos com uma violação isolada produzem seu erro específico. Panic, diagnóstico de sanitizer e divergência do oráculo serão classificados separadamente. |
| O target é determinístico e não transmite estado entre chamadas. | Repetições da mesma entrada e execuções intercaladas com outras entradas mantêm resultado e diagnóstico, com recursos liberados a cada chamada. |
| Um reproducer pode ser reduzido sem trocar a classe de defeito investigada. | A entrada menor mantém a mesma violação e o diagnóstico correspondente; uma redução que muda a causa será recusada ou registrada como outro caso. |
| A correção remove a causa identificada preservando o comportamento válido. | O reproducer original, o reduzido, as regressões independentes e as entradas vizinhas cumprem o contrato após a mudança. |

Antecipe também quais partes do formato cada seed deverá alcançar. Uma campanha sem descobertas é uma observação possível dentro do orçamento; não constitui hipótese confirmada de ausência de defeitos.

### Conduzir os experimentos

1. Escreva casos de aceitação e rejeição a partir da tabela, sem consultar a lógica interna do parser. Registre resultados esperados e hipóteses antes de observar a implementação.
2. Prepare seeds pequenas que alcancem registros numéricos, texto e checksum; explique a contribuição esperada de cada uma.
3. Execute repetidamente a mesma entrada, inclusive entre outras entradas, e confira determinismo e liberação de recursos.
4. Registre a campanha e seus limites reais, classifique cada artefato e reproduza-o isoladamente. Preserve os artefatos antes de reiniciar após uma falha.
5. Para cada defeito não descoberto, consulte o reproducer de reserva no kit público e registre sua origem. Os dois defeitos devem entrar na investigação, independentemente da descoberta espontânea.
6. Minimize pelo menos um caso conferindo se o diagnóstico e a identidade do defeito permanecem os mesmos.
7. Explique a invariante violada e corrija sua causa. Confronte a previsão da correção com o comportamento observado.
8. Acrescente regressões e entradas vizinhas; repita a execução sem fuzzing, com resultados calculados independentemente do parser. Relacione hipóteses, evidências, explicação do mecanismo e limites da conclusão.

### Registrar as evidências

Harness, corpus comentado, manifesto da campanha, artefatos originais e reduzidos, diagnóstico, correções e regressões. O runner funciona sem fuzzing e confere resultados calculados independentemente do parser. Relate limitações e efeitos sobre entradas válidas.

Inclua o registro das hipóteses e previsões, a origem de cada reproducer, a comparação antes/depois de cada correção e a ligação entre sintoma, invariante violada e teste de regressão. A explicação deve mostrar por que a minimização preservou o defeito e por que os resultados do oráculo não dependem da lógica do parser investigado.

### Explicar e delimitar

Diferencie entrada rejeitada conforme o contrato, defeito observado, defeito encontrado espontaneamente e defeito investigado a partir de reproducer fornecido. Os dois últimos caminhos permitem concluir sobre o mecanismo analisado; somente o registro da campanha permite atribuir uma descoberta ao fuzzing.

Ausência de crash no orçamento fixado não comprova correção. Um sanitizer sem diagnóstico não descarta erros lógicos, e um erro retornado pelo parser só é aceitável quando corresponde ao contrato. A interpretação depende do oráculo independente e da classe de defeito que cada ferramenta observa.

A minimização sustenta uma explicação mais localizada quando preserva a identidade do defeito; uma entrada menor, por si só, não prova essa preservação. Regressões e entradas vizinhas sustentam a correção dos comportamentos verificados. Registre o alcance dessa evidência sem apresentar uma campanha limitada ou um conjunto de testes como prova geral de ausência de falhas.

## Critérios de conclusão

- Documento vazio válido com `count=0` e `payload_length=0`, com e sem checksum.
- Um registro numérico `65535` e dois desses registros somando `131070`.
- Texto de zero e de 32 bytes; rejeição de byte `0x1f`, `0x7f` e comprimento 33.
- Cabeçalho truncado, dados de registro truncados, tipo desconhecido, contagem inconsistente, flag reservada, checksum incorreto e byte extra.
- Entrada de 4097 bytes retorna `TooLarge` sem tentativa de parsing.
- Dois defeitos reproduzidos e corrigidos; pelo menos um caso minimizado com identidade do defeito preservada.
- Regressões passam em execução determinística. A campanha e seus limites ficam documentados mesmo quando nenhum crash foi descoberto espontaneamente.

Em C, use ASan e UBSan no build de investigação e registre opções efetivas. ASan cobre classes de acesso inválido; UBSan instrumenta classes selecionadas de undefined behavior. Nenhum dos dois substitui um oráculo para OXF1 ([ASan](https://clang.llvm.org/docs/AddressSanitizer.html), [UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)).

A conclusão exige relacionar as hipóteses às observações e explicar os dois mecanismos de falha, as correções e seus limites. A presença de um harness, de crashes ou de uma versão corrigida, isoladamente, não encerra a investigação.

Uma previsão refutada pode ser um resultado válido. Erro de preparação, instrumento incorreto ou timeout não classificado não responde à pergunta experimental. Registre requisitos bloqueados e repita-os em ambiente compatível antes de concluir o núcleo.

## Extensões opcionais

Fuzzing diferencial entre C e Rust, mutadores conscientes do formato e redução do corpus por cobertura são extensões. Uma proposta de CI deve executar rapidamente regressões determinísticas; campanhas longas recebem orçamento separado. Esta ficha especifica esse comportamento, sem afirmar que uma pipeline já existe ou foi executada.

## Participação no clube

Compartilhe código e relato em seu próprio repositório. Apresente a pergunta, a previsão inicial, uma entrada pequena, os comandos e as evidências na conversa do clube. Você pode compartilhar uma tentativa incompleta; identifique o que ainda não foi executado ou explicado.

Use o [modelo de relato](report-template.md). Preserve o limite de páginas indicado nos entregáveis, quando houver; mantenha código, logs e dados extensos em arquivos próprios.

## Referências e atividades relacionadas

As [leituras orientadas](references.md) indicam documentação e código real. Relacione a investigação aos conhecimentos prévios e às atividades citadas, sem tratá-las como uma sequência obrigatória. Os IDs em prosa identificam atividades do catálogo; propostas em elaboração não equivalem a materiais já publicados.
