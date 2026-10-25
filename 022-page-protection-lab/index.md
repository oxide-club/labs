---
title: "Laboratório de Page protection e access violations"
area: "memory"
slug: "022-page-protection-lab"
summary: "Investigue permissões de páginas com sondas isoladas e uma matriz de previsões e resultados."
question: "O que distingue um endereço numérico, uma página mapeada e uma operação permitida naquela página?"
draft: true
topics: ["Memória virtual", "Page protection", "Processos"]
prerequisites: ["Ponteiros", "Memória virtual", "Processos e sinais", "Disassembly"]
tools: ["Compilador C", "objdump", "/proc"]
environment: "Linux x86-64; C, usuário comum, processos próprios e toolchain registrada"
difficulty: advanced
---

## O que vamos investigar

Investigue a relação entre endereço, mapeamento e permissão de acesso. Implemente `pageprobe` como instrumento experimental para executar uma tentativa de leitura ou escrita por subprocesso, sobre uma região criada pelo próprio experimento. Antes de executar, registre sua previsão. Compare o resultado com as permissões solicitadas e observadas, explique divergências e apresente uma demonstração em que o supervisor continua funcionando após uma falha esperada.

Use a sonda nativa revisada pelo clube para as operações deliberadamente proibidas. Inspecione seu disassembly. Essas sondas investigam a resposta do SO a uma instrução; não demonstram que acessar memória inválida seja comportamento definido em C ou Rust. `volatile` não transforma uma operação inválida em operação segura.

### Por que investigar este mecanismo

Uma região mapeada não autoriza qualquer operação sobre seus bytes. O laboratório relaciona syscall, permissões e resultado de acesso, preparando o estudo de guard pages, NX e W^X sem geração de código.

O objetivo também é aprender a conduzir experimentos que podem falhar: a falha esperada de um filho deve produzir uma medição útil, sem derrubar o supervisor ou travar a sessão. A documentação de [`mprotect`](https://man7.org/linux/man-pages/man2/mprotect.2.html) distingue permissões solicitadas e particularidades de arquitetura; portanto, a matriz não deve presumir que toda combinação de flags corresponda a uma capacidade independente do hardware.

### Objetivos de aprendizagem

- Construir uma matriz de quatro configurações de proteção e duas operações, identificando expectativa, observação e divergência.
- Relacionar endereços, tamanho de página e intervalo afetado por uma mudança de proteção.
- Distinguir erro de preparação, terminação normal, sinal e timeout do subprocesso.
- Sustentar uma conclusão sobre permissões com registros de syscall e de mapeamento.
- Explicar o alcance local de W^X e por que este experimento não comprova a política de todo o processo ou sistema.
- Explicar os resultados por meio de hipóteses verificáveis, distinguindo o mecanismo observado dos limites impostos pela linguagem e pelo ambiente.

### Conceitos trabalhados

Mapeamentos anônimos, granularidade de páginas, `mmap`, `mprotect`, `munmap`, isolamento de falhas e supervisão. O participante trabalhará também com hipóteses experimentais, evidência negativa e classificação de ambientes incompatíveis. [`mmap`](https://man7.org/linux/man-pages/man2/mmap.2.html) será estudado como interface de mapeamento, sem tratar a região obtida como equivalente a um objeto comum de `malloc`.

### Contrato técnico

O programa aceitará `--case all|<id>` e `--timeout-ms N`, com `N` entre 100 e 10.000; padrão de 2.000 ms. Argumentos inválidos devem falhar antes de criar filhos. Cada filho criará uma região de três páginas anônimas privadas, inicializada enquanto gravável; apenas a página central será objeto da sonda. O tamanho de página será consultado no ambiente, sem constante presumida.

Execute a matriz abaixo, com região e filho novos para cada operação. Inicialize o byte como `0xA5`; a escrita tentará substituí-lo por `0x5A`. Os resultados obrigatórios independem da previsão do participante.

| Proteção | Leitura | Escrita |
|---|---|---|
| `PROT_NONE` | `SIGSEGV` obrigatório | `SIGSEGV` obrigatório |
| `PROT_READ` | `ok`, byte `0xA5` | `SIGSEGV` obrigatório |
| `PROT_WRITE` | Observacional: `ok`/`0xA5` ou `SIGSEGV` | `ok` obrigatório |
| `PROT_READ\|PROT_WRITE` | `ok`, byte `0xA5` | `ok` obrigatório |

Acrescente `RW → R → RW`, verificando preservação e restauração da escrita. Nenhuma etapa solicitará `PROT_EXEC` ou executará dados.

Registre por caso identificador, proteção solicitada, permissões observadas, operação, duração, resultado e detalhe. Resultados: `ok`, `signal`, `setup_error`, `timeout` e `unsupported`, com código de saída, sinal e `errno` separados. O supervisor retornará 0 quando todos os casos selecionados cumprirem os resultados esperados, incluindo os erros intencionais de `unaligned` e `zero-length` e o timeout esperado de `hang`. Retornará 1 para divergência e 2 para erro **inesperado** de preparação ou ambiente incompatível. O caso observacional deve ser classificado conforme a matriz. Na agregação, 2 tem precedência sobre 1, que tem precedência sobre 0. Este refinamento foi aprovado pelo responsável em 25/10/2026, nesta conversa de preparação.

Nas sondas proibidas do alvo declarado, investigue `SIGSEGV`; não traduza qualquer saída diferente de zero como esse sinal. Use o status real de espera, conforme [`waitpid`](https://man7.org/linux/man-pages/man2/waitpid.2.html). Um timeout exige encerrar o filho, coletar seu status e continuar; não será registrado como falha de proteção.

Inclua um caso de endereço não alinhado em `mprotect`, outro de `mmap` com comprimento zero e uma sonda de teste que permanece aguardando. Verifique erros sem acessar a região quando a preparação falhar. Não deixe filhos ou descritores pendentes. A política local exigirá ausência de `x` no mapeamento testado; se o ambiente conceder execução implicitamente, registre incompatibilidade, sem modificar configurações globais.

## Antes de começar

Ponteiros, bytes, aritmética verificada, processos, sinais, códigos de saída e `/proc`. Saber compilar C, ler disassembly e distinguir contrato da linguagem de observação numa plataforma. Familiaridade com heap allocation ajuda, mas não substitui memória virtual.

### Linguagens e ambiente

Linux x86-64; C, usuário comum, processos próprios e toolchain registrada.

C é a linguagem-base do núcleo. As alternativas indicadas nas extensões são complementares.

**Em elaboração.** O pacote inicial e os checks estão preparados. O [guia local](README.md) registra comandos, ambiente observado e limites. A publicação depende de revisão e piloto.

## Materiais

Leia o [inventário dos materiais](materials/README.md). O pacote inclui supervisor C incompleto, sonda assembly auditada, matriz vazia e checks comportamentais. Consulte o [formato dos registros](materials/records.md) e a [auditoria da sonda](materials/audit.md). Use o [modelo de relato](report-template.md).

O refinamento operacional distingue os controles intencionais: `all` retorna 0 quando os erros de preparação esperados e o timeout são conferidos, junto aos resultados obrigatórios. Erro inesperado de preparação ou ambiente incompatível continua retornando 2; divergência retorna 1. IDs e tolerância do timeout estão no contrato dos registros. A [descrição da VM](materials/vm.md) fixa distribuição, recursos e preparação. O guia identifica os ambientes efetivamente verificados.

## Etapas da investigação

Registre previsões antes de executar. Preserve entradas, comandos e resultados para explicar o mecanismo e os limites de cada conclusão.

### Prever

Antes de executar as sondas, registre uma previsão para cada caso e associe-a ao resultado que será medido. As exigências da matriz permanecem independentes de uma previsão inicial correta ou incorreta.

| Hipótese verificável | Previsão e evidência |
|---|---|
| A proteção da página central controla o resultado da operação testada no ambiente declarado. | `PROT_NONE` impede leitura e escrita; `PROT_READ` permite ler `0xA5` e impede escrever; `PROT_READ\|PROT_WRITE` permite ambas. Confronte permissões observadas, operação e status real do filho. |
| `PROT_WRITE` permite escrita, mas não define uma conclusão universal sobre leitura. | A escrita deve funcionar. Para leitura, registre a previsão específica para o ambiente e aceite como observação classificável `ok`/`0xA5` ou `SIGSEGV`, sem exigir que a página seja “write-only”. |
| Alterar `RW → R → RW` preserva os dados e permite restaurar a escrita. | O conteúdo permanece verificável e a última etapa permite nova escrita, sem solicitar execução. |
| Preparação inválida e espera excedida são mecanismos distintos de falha de proteção. | `mprotect` com endereço não alinhado e `mmap` com comprimento zero produzem erros de preparação sem acesso posterior; a sonda que aguarda produz timeout, seguido do encerramento e do child reaping. |
| Isolar cada sonda em um filho permite continuar o experimento após uma falha esperada. | O supervisor registra o sinal ou timeout, libera recursos e executa o caso seguinte normalmente. |

Considere também a possibilidade de ambiente incompatível: uma concessão implícita de execução viola a política local do experimento e deve ser registrada, sem alterar configurações globais.

### Conduzir os experimentos

1. Desenhe as três páginas e indique a origem de cada endereço utilizado; consulte o tamanho de página e inspecione o disassembly da sonda nativa revisada pelo clube.
2. Preencha expectativas antes dos testes, marcando o caso `PROT_WRITE`/leitura como dependente da plataforma. Defina quais registros distinguem sinal, erro de preparação e timeout.
3. Prepare uma região e um filho novos para cada operação. Observe o mapeamento após a mudança de proteção e antes da sonda.
4. Compare os oito resultados e a sequência de transições; separe falhas da ferramenta de falhas intencionais. Para cada divergência, confronte proteção solicitada, permissões observadas e status real de espera.
5. Execute os casos de alinhamento e comprimento inválidos sem acessar a região quando a preparação falhar.
6. Injete a espera controlada e demonstre que o prazo do supervisor funciona, que o filho é encerrado e devidamente finalizado e que o próximo teste executa normalmente.
7. Relacione as previsões aos resultados e explique o que sua evidência informa sobre páginas e o que não informa sobre segurança de memória da linguagem. Confira o encerramento de todos os recursos.

### Registrar as evidências

Código e instruções de build; matriz preenchida; registros de todos os casos; trechos relevantes de mapeamentos e disassembly; relatório de até três páginas explicando três previsões confirmadas ou corrigidas. Inclua versões de kernel, arquitetura, compilador e flags, além de um inventário de recursos encerrados.

A matriz deve separar hipótese, previsão, observação e interpretação, incluindo a leitura sob `PROT_WRITE`. O relatório deve vincular cada uma das três previsões discutidas a registros do mapeamento, da operação e do status do filho, explicando o mecanismo e os limites da conclusão.

### Explicar e delimitar

A matriz permite relacionar uma instrução de leitura ou escrita, as permissões solicitadas e observadas e a resposta do SO no ambiente registrado. A classificação deve usar o status real do filho: saída diferente de zero, erro de preparação e timeout não equivalem automaticamente a `SIGSEGV`.

O resultado de leitura sob `PROT_WRITE` permanece observacional. Ele informa como aquela configuração se comportou na plataforma, sem estabelecer independência universal entre permissões de leitura e escrita. Uma previsão corrigida é um resultado válido quando a evidência e a explicação são consistentes.

A sonda nativa estuda a resposta a uma instrução, sem tornar definido em C ou Rust o acesso a memória inválida. `volatile` não altera esse limite. A ausência de `x` ou de `RWX` no mapeamento testado sustenta somente uma conclusão sobre a região e os instantes observados; não demonstra W^X para o processo ou o sistema inteiro. O experimento não solicita `PROT_EXEC` nem executa dados.

## Critérios de conclusão

- Leitura e escrita autorizadas preservam o padrão esperado; a transição de volta a `RW` permite nova escrita.
- Casos proibidos terminam somente o filho e registram o sinal real.
- `PROT_WRITE` não é interpretado automaticamente como “write-only”: leitura bem-sucedida pode ser uma observação correta da plataforma.
- Erros de alinhamento e tamanho são classificados antes de qualquer acesso.
- O caso de espera termina por timeout dentro da tolerância declarada, com status coletado; o teste seguinte executa normalmente.
- Não há endereços absolutos nas fixtures nem conclusão universal baseada numa execução.

A conclusão requer a matriz completa e a explicação das previsões confirmadas ou corrigidas. Classificar uma leitura bem-sucedida sob `PROT_WRITE` como observação válida faz parte do experimento; não se exige provocar sua falha.

Uma previsão refutada pode ser um resultado válido. Erro de preparação, instrumento incorreto ou timeout não classificado não responde à pergunta experimental. Registre requisitos bloqueados e repita-os em ambiente compatível antes de concluir o núcleo.

## Extensões opcionais

Extensões possíveis: guard pages, copy-on-write e comparação com outra arquitetura. Execução dinâmica/JIT fica fora desta ficha. Ausência de páginas `RWX` na região observada sustenta apenas uma afirmação sobre aquela região e aqueles instantes; não comprova W^X global. Conexões: fundamentos de memória virtual e laboratório `023-elf-hardening-lab`.

## Participação no clube

Compartilhe código e relato em seu próprio repositório. Apresente a pergunta, a previsão inicial, uma entrada pequena, os comandos e as evidências na conversa do clube. Você pode compartilhar uma tentativa incompleta; identifique o que ainda não foi executado ou explicado.

Use o [modelo de relato](report-template.md). Preserve o limite de páginas indicado nos entregáveis, quando houver; mantenha código, logs e dados extensos em arquivos próprios.

## Referências e atividades relacionadas

As [leituras orientadas](references.md) indicam documentação e código real. Relacione a investigação aos conhecimentos prévios e às atividades citadas, sem tratá-las como uma sequência obrigatória. Os IDs em prosa identificam atividades do catálogo; propostas em elaboração não equivalem a materiais já publicados.
