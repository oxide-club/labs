# Português Técnico Claro (PTC)

**Convenção editorial do Oxide Club — versão 1.0**\
**Data:** 25 de outubro de 2026\
**Aplicação:** agentes de IA, autores, revisores e mantenedores de conteúdo\
**Local sugerido:** `docs/guia-de-redacao.md`

> **Status:** convenção editorial adotada neste repositório por solicitação do responsável. Este documento define como escrever e revisar os materiais do Oxide Club. Não é uma tradução, certificação nem implementação do ASD-STE100.

## 1. Finalidade

O **Português Técnico Claro (PTC)** é uma convenção editorial para conteúdos técnicos em português brasileiro. Seu objetivo é tornar enunciados, notas, documentação e instruções **fáceis de ler, precisos e consistentes**.

O PTC toma como inspiração a ideia de linguagem controlada do *ASD-STE100 (Simplified Technical English)* e práticas de linguagem simples. Suas regras, porém, foram formuladas para o português e para o contexto de Ciência da Computação do Oxide Club.

**Princípio central:** simplifique a escrita, não o mecanismo técnico.

Uma explicação é boa quando o leitor consegue identificar o que fazer, por que fazer, o que observar e quais conclusões os resultados sustentam. Uma frase curta, mas tecnicamente falsa ou incompleta, não atende ao PTC.

### 1.1. Onde aplicar

Esta convenção se aplica a:

- Laboratórios, desafios e roteiros de experimentação.
- Notas técnicas e textos explicativos.
- Documentação de repositórios, guias de contribuição e instruções para participantes.
- Mensagens de erro, comentários instrutivos e texto de interface redigidos para o clube.
- Textos e revisões produzidos por agentes de IA.

Ela **não** exige reescrever código-fonte de terceiros, citações diretas, nomes oficiais de APIs, especificações externas ou texto cujo formato exato faça parte de um contrato. Nesses casos, preserve o material original e explique-o em PTC ao redor dele.

### 1.2. O que o PTC não pretende fazer

- Eliminar termos técnicos.
- Proibir frases longas em qualquer circunstância.
- Impor uma lista fechada de palavras comuns.
- Transformar documentos de sistemas em textos publicitários ou excessivamente informais.
- Alterar contratos, interfaces, condições ou resultados para facilitar a leitura.
- Substituir revisão técnica por uma ferramenta de legibilidade.

## 2. Hierarquia de decisões

Quando duas orientações entrarem em conflito, siga esta ordem:

1. **Correção técnica e fidelidade às fontes:** preserve fatos, pré-condições, pós-condições, fórmulas, APIs, comportamento e limites documentados.
2. **Contratos e convenções do projeto:** respeite especificações vigentes, nomes canônicos, decisões terminológicas e requisitos de publicação.
3. **Clareza e ausência de ambiguidade:** deixe explícitos agentes, condições, ações e resultados.
4. **Consistência editorial:** use os termos e formatos definidos neste documento e no glossário.
5. **Concisão e fluidez:** reduza palavras e repetições sem perder os itens anteriores.

Em particular, **não sacrifique correção para atingir um número arbitrário de palavras por frase**.

## 3. Linguagem normativa

Nos enunciados e contratos, use os verbos modais de forma consistente:

| Expressão | Significado editorial | Exemplo |
| --- | --- | --- |
| **deve** | Requisito obrigatório | “A função deve retornar `NULL` quando não houver espaço.” |
| **não deve** | Comportamento proibido | “O programa não deve desreferenciar os endereços do trace.” |
| **recomenda-se** | Orientação não obrigatória | “Recomenda-se executar os testes com AddressSanitizer.” |
| **pode** | Opção permitida | “Você pode usar GDB para inspecionar os registradores.” |

**Regras:**

- Não alterne `deve`, `deveria`, `precisa` e `é importante` quando estiver expressando o mesmo requisito.
- Se uma escolha afetar a correção, escreva-a como requisito e informe como verificar seu cumprimento.
- Use `somente`, `exatamente`, `pelo menos`, `no máximo` e `antes/depois` quando essas restrições fizerem parte do contrato.
- Não use `sempre`, `nunca`, `garante` ou `prova` sem condições suficientes para sustentar a afirmação.
- Diferencie **fato observado**, **hipótese**, **expectativa do contrato** e **garantia demonstrada**.

## 4. Regras de redação

### PTC-01 — Uma ideia principal por frase

Divida frases que misturem instrução, justificativa, exceção e resultado. Não fragmente expressões cuja relação lógica precisa permanecer explícita.

**Evite:** “Após a compilação do programa, execute o binário, analise a saída e, considerando a possibilidade de falhas de allocation, verifique se o resultado corresponde às expectativas.”

**Prefira:** “Compile o programa e execute o binário. Registre a saída. Depois, teste o caso em que a allocation falha.”

### PTC-02 — Frases curtas, sem limite rígido

Use cerca de **20 palavras por frase como sinal de revisão**, não como critério mecânico de aprovação. Frases maiores são aceitáveis quando tornam condições ou relações técnicas mais claras.

Não divida uma condição de segurança em fragmentos que mudem sua interpretação.

### PTC-03 — Ordem direta e sujeito identificado

Prefira sujeito → verbo → complemento. Especifique quem realiza a ação: participante, programa, compilador, linker, loader, kernel ou ferramenta.

**Evite:** “Após a validação, será retornado um erro.”\
**Prefira:** “Se o alinhamento for inválido, `arena_alloc` deve retornar `NULL`.”

### PTC-04 — Voz ativa por padrão

Use voz ativa quando o agente for conhecido e relevante.

**Evite:** “Os argumentos são verificados pela função.”\
**Prefira:** “A função verifica os argumentos.”

Use voz passiva quando o agente não importar ou quando ela favorecer a precisão: “O processo foi encerrado por um sinal.”

### PTC-05 — Verbo de ação em instruções

Comece passos práticos com verbos como **compile, execute, implemente, calcule, observe, compare, registre, identifique, explique, verifique**.

**Evite:** “Proceda à execução dos testes.”\
**Prefira:** “Execute os testes.”

### PTC-06 — Uma ação verificável por etapa

Separe tarefas independentes em passos distintos. Cada passo deve indicar, quando cabível, **entrada, ação e resultado esperado**.

**Exemplo:** “Execute `./cache < trace-a.txt`. Verifique se a saída contém `hits=3 misses=5 evictions=3`.”

### PTC-07 — Nomes concretos em vez de abstrações vagas

Prefira **função, ponteiro, byte, bloco, registrador, arquivo, processo, thread e campo** a expressões como “elemento”, “estrutura em questão” ou “mecanismo supracitado” quando o objeto puder ser nomeado.

**Evite:** “A operação deve atualizar a estrutura correspondente.”\
**Prefira:** “Após uma allocation válida, `arena_alloc` deve atualizar `used`.”

### PTC-08 — Elimine formalismo sem função

Evite construções como **proceder à**, **efetuar a**, **realizar a implementação de**, **no que tange a**, **cabe ressaltar que**, **vale mencionar que**, **nesse sentido** e **de forma a possibilitar** quando não acrescentarem informação.

### PTC-09 — Use o mesmo termo para o mesmo conceito

Não varie a terminologia apenas para evitar repetição. Se `object file` for o termo escolhido, mantenha-o ao longo do texto. Use palavras diferentes somente quando houver diferença de significado.

### PTC-10 — Introduza conceitos sem esconder a definição

Na primeira ocorrência relevante de um termo novo:

1. Explique a ideia em linguagem direta.
2. Dê a definição técnica necessária ao laboratório.
3. Mostre um exemplo pequeno, se isso ajudar.
4. Depois, use o termo normalmente.

**Exemplo:** “Uma *data race* envolve acessos conflitantes ao mesmo local de memória, sem a sincronização exigida pelo modelo da linguagem, e pelo menos um acesso modifica esse local. Em C, esse defeito produz comportamento indefinido.”

Não repita a definição inteira a cada ocorrência.

### PTC-11 — Afirme apenas o que a evidência sustenta

Use expressões delimitadoras quando necessárias: **neste modelo**, **para estas entradas**, **nesta execução**, **nesta arquitetura**, **com estas flags**, **sob as hipóteses descritas**.

**Evite:** “A ordem dos loops por linhas é sempre mais rápida.”\
**Prefira:** “Neste experimento, o percurso por linhas produziu menos misses no simulador.”

### PTC-12 — Explique a condição antes da consequência

Em contratos, prefira “Se [condição], [comportamento]”. Evite referências vagas a “casos anteriores” ou “essa situação”.

**Exemplo:** “Se `size` for zero, `arena_alloc` deve retornar `NULL` sem alterar `used`.”

### PTC-13 — Separe previsão, observação e conclusão

Uma hipótese não é um resultado. Um trace não é uma explicação. Uma execução sem erro não constitui prova geral de correção.

Use rótulos claros quando necessário: **Hipótese**, **Comando**, **Resultado esperado**, **Resultado observado**, **Explicação**, **Limitação**.

### PTC-14 — Evite analogias que substituem o mecanismo

Analogias podem introduzir uma ideia, mas não podem representar um contrato técnico no lugar de sua definição. Quando uma analogia for usada, delimite seu alcance.

### PTC-15 — Escreva português natural

Prefira “se”, “quando”, “antes”, “depois” e “porque” a nominalizações artificiais. Não produza uma tradução palavra por palavra da documentação inglesa.

**Evite:** “A função realiza uma verificação de disponibilidade de capacidade.”\
**Prefira:** “A função verifica se há espaço suficiente.”

## 5. Vocabulário técnico controlado

O texto corrido deve ser escrito em **português brasileiro**. Mantenha os termos ingleses abaixo, já adotados pelo Oxide Club, quando estiverem sendo usados com sentido técnico.

### 5.1. Termos fixados

| Usar | Evitar como substituição automática | Observação |
| --- | --- | --- |
| `syscall` / `syscalls` | chamada(s) ao sistema | Diferencie syscalls de funções da libc. |
| operadores bitwise | operadores bit a bit | Para `&`, `\|`, `^`, `~`, `<<`, `>>` quando operarem sobre bits. |
| disassembly | desmontagem | Para a representação textual de instruções de máquina. |
| stack | pilha | Em contexto de execução, memória e calling conventions. |
| lifetime | tempo de vida | Para validade e duração de objetos ou referências. |
| calling conventions | convenções de chamada | Para contratos de passagem de argumentos e preservação de estado. |
| object file | arquivo objeto | Para o artefato produzido na compilação/montagem antes do linking final. |
| linking | ligação | Para o processo de composição de objetos e resolução de símbolos. |
| static linking | ligação estática | Quando se tratar dessa modalidade. |
| dynamic linking | ligação dinâmica | Quando se tratar dessa modalidade. |
| dynamic loader | carregador dinâmico | Para o componente responsável pelo carregamento dinâmico. |

A tabela fixa **escolhas editoriais**, não equivalências universais. Preserve nomes oficiais de ferramentas, mensagens e especificações externas.

### 5.2. Termos aceitos conforme o contexto

Os termos abaixo **podem permanecer em inglês** quando forem usuais na documentação consultada ou mais precisos no contexto: `heap`, `buffer`, `thread`, `stack frame`, `cache hit`, `cache miss`, `data race`, `race condition`, `deadlock`, `race`, `trace`, `runtime`, `benchmark`, `profiling`, `parser`, `payload`, `framing`, `bytecode`, `waker`, `pool allocator`, `arena allocator`, `memory mapping`, `use-after-free`, `overflow` e `underflow`.

Não se trata de uma lista de palavras que obrigatoriamente devam ficar em inglês. Escolha uma forma e mantenha-a no documento, sem comprometer diferenças semânticas.

### 5.3. Português preferido quando natural e preciso

Use normalmente: **ponteiro, registrador, memória virtual, processo, arquivo, endereço, alinhamento, deslocamento, bloco, campo, segmento, seção, execução, compilador, função, biblioteca, sinal, resultado, hipótese, evidência, erro e invariante**.

Não transforme uma preferência por termos técnicos ingleses em um texto misturado sem critério.

### 5.4. Distinções que não podem desaparecer

- **Syscall × função de biblioteca:** chamar `read()` pela libc não significa que toda função da libc seja uma syscall.
- **API × ABI:** interface de programação não é o mesmo que contrato binário.
- **Stack × heap:** são mecanismos ou regiões com propriedades diferentes; não use um pelo outro.
- **Seção de ELF × segmento de ELF:** não são estruturas equivalentes.
- **Endereço virtual × offset de arquivo:** números associados a espaços distintos.
- **Data race × race condition:** uma data race tem significado específico no modelo de memória; race condition é mais amplo.
- **Concorrência × paralelismo:** progresso por interleavings não implica execução simultânea em múltiplas unidades.
- **Cache miss simulado × cache miss medido:** não confunda resultados de modelos com contadores do hardware.
- **Observação × prova:** não inferir garantia universal de um conjunto pequeno de execuções.

### 5.5. Termos ainda não decididos

Se encontrar uma tradução ambígua que afete vários documentos, **não imponha uma preferência silenciosamente**. Registre:

1. Termo original em inglês.
2. Alternativas em português e inglês.
3. Contexto técnico.
4. Proposta e justificativa.
5. Status: **proposto** ou **aprovado**.

Use o glossário canônico para registrar decisões aprovadas. Se não houver orientação, mantenha provisoriamente o termo técnico usual e sinalize a decisão pendente para revisão editorial.

## 6. Escrita de contratos técnicos

Enunciados e especificações devem permitir implementar e verificar um comportamento sem adivinhações.

### 6.1. Especifique o comportamento

Sempre que aplicável, defina:

- Entrada e formato.
- Saída e formato.
- Pré-condições.
- Pós-condições.
- Faixas aceitas e limites.
- Erros e estados após falhas.
- Invariantes.
- Ambiente de referência.
- Comportamentos explicitamente fora do escopo.

**Exemplo insuficiente:** “O alocador deve tratar erros corretamente.”

**Exemplo adequado:** “Se `alignment` não for potência de dois, `arena_alloc` deve retornar `NULL` sem alterar `used`.”

### 6.2. Não esconda exceções

Se uma regra tiver exceções, indique-as perto da regra ou por referência inequívoca. Evite expressões vagas como “conforme necessário” e “tratamento adequado” quando houver comportamento verificável.

### 6.3. Não prometa portabilidade inexistente

Declare arquitetura, sistema operacional, ABI, compilador e flags quando resultados dependerem desses fatores. Evite fixar endereços, PIDs, registradores concretos ou mensagens de diagnóstico não estáveis, salvo se forem parte do contrato de um ambiente específico.

### 6.4. Identifique o tipo de resultado

Diferencie:

- **Resultado normativo:** saída exigida pelo contrato.
- **Resultado ilustrativo:** exemplo possível, mas não garantido.
- **Resultado observado:** medição ou trace registrado num ambiente conhecido.
- **Hipótese:** previsão ainda não verificada.

## 7. Organização dos materiais por modalidade

### 7.1. Laboratórios e desafios

Prefira esta sequência, ajustada ao objetivo:

1. Pergunta central.
2. O que será investigado.
3. Conhecimentos prévios.
4. Ambiente e preparação.
5. Contrato ou fenômeno de interesse.
6. Etapas: prever, observar, explicar, implementar/corrigir, verificar.
7. Critérios de conclusão.
8. Extensões opcionais.
9. Referências e code reading.

Em cada etapa, deixe explícito **o que fazer** e **o que entregar ou observar**. Não esconda requisitos obrigatórios em seções de aprofundamento.

### 7.2. Notas técnicas

Use, quando apropriado, **pergunta/problema → mecanismo → evidência → limites → implicações**. Explique conceitos antes de apresentar detalhes de implementação que dependam deles. Não use tom de tutorial se a finalidade for uma investigação técnica.

### 7.3. Documentação operacional

Dê prioridade a instruções executáveis, pré-requisitos, comandos, resultados esperados e formas de recuperação em caso de erro.

### 7.4. Referências de código real

Para cada referência, informe **o que o arquivo implementa**, **o que observar**, **como difere do exercício** e **uma pergunta de leitura**. Evite links sem explicação.

## 8. Formatação, código e exemplos

- Use headings descritivos. Prefira “Como executar os testes” a “Considerações gerais”.
- Use listas quando houver passos, alternativas ou itens que precisam ser conferidos. Não transforme todo o documento em listas.
- Use tabelas para contratos, campos binários, casos de teste e comparações genuinamente tabulares.
- Formate identificadores, comandos, flags, caminhos, valores de retorno e saídas literais com código Markdown.
- Forneça blocos de código com linguagem declarada quando isso ajudar a leitura.
- Separe comandos de exemplos de saída; não faça o leitor adivinhar o que deve digitar.
- Preserve maiúsculas, pontuação e bytes quando fizerem parte da verificação exata.
- Não use imagens, diagramas ou formatação ornamental no lugar de especificações necessárias.
- Links devem ter contexto: explique por que a fonte é relevante e o que o leitor encontrará nela.
- Não atribua a uma fonte conclusões que ela não sustenta. Não invente comandos executados, benchmarks ou resultados de testes.

### Mensagens de erro e diagnósticos

Quando o texto for controlado pelo projeto, prefira mensagens específicas e acionáveis.

**Evite:** `Erro ao processar entrada.`\
**Prefira:** `Erro: alinhamento deve ser uma potência de dois.`

Não altere mensagens literais exigidas por fixtures ou por interfaces externas.

## 9. Antes e depois: padrões de revisão

| Evitar | Preferir | Motivo |
| --- | --- | --- |
| “Proceda à execução do programa.” | “Execute o programa.” | Verbo direto. |
| “Efetue a allocation de uma região de memória.” | “Aloque uma região de memória.” | Menos nominalização. |
| “Subsequentemente, proceda à verificação dos resultados.” | “Depois, verifique os resultados.” | Ordem temporal clara. |
| “Uma falha poderá ocorrer nessa situação.” | “Se a arena estiver cheia, a função deve retornar `NULL`.” | Condição e resultado explícitos. |
| “O uso de memória após deallocation constitui uma condição adversa.” | “Ler dados depois de liberar sua memória causa um use-after-free.” | Nomeia o defeito. |
| “A implementação deverá se encarregar da inicialização das estruturas.” | “Inicialize as estruturas antes do primeiro acesso.” | Agente e momento explícitos. |
| “Uma cache tem bom desempenho por causa de sua velocidade.” | “Uma cache pode reduzir o custo de acessos quando o programa reutiliza dados.” | Explicação causal, com limites. |
| “O teste provou que não há bugs.” | “O teste não encontrou falhas nos casos executados.” | Não amplia a evidência. |
| “A estrutura foi escrita em disco.” | “O programa gravou os quatro bytes do header em little-endian.” | Representação e ação explícitas. |
| “O programa deverá executar corretamente em qualquer ambiente.” | “O laboratório usa Linux x86-64 como ambiente de referência.” | Declara escopo de portabilidade. |

## 10. Procedimento obrigatório para agentes

Todo agente que criar ou revisar conteúdo do Oxide Club **deve** seguir este procedimento.

### Etapa 1 — Ler e delimitar

1. Identifique o tipo de documento e seu público.
2. Leia os contratos, arquivos e fontes necessários.
3. Identifique requisitos normativos e dados que não podem mudar.
4. Consulte este guia e o glossário aprovado.

### Etapa 2 — Redigir

1. Estruture a explicação pela ordem em que o leitor precisa da informação.
2. Use verbos diretos e sujeitos identificáveis.
3. Defina conceitos novos no ponto adequado.
4. Escreva condições, comportamentos e resultados de forma verificável.
5. Preserve terminologia, código, comandos e valores literais.

### Etapa 3 — Revisar em duas passagens independentes

**Revisão técnica:** confira fatos, semântica, contratos, exemplos, condições, resultados, referências e limitações.

**Revisão editorial:** confira clareza, frases longas, voz, consistência de termos, instruções, redundâncias e organização.

Uma revisão editorial **não pode** mudar um contrato sem uma revisão técnica correspondente.

### Etapa 4 — Registrar pendências

Se um contrato estiver ambíguo, uma fonte for inacessível ou uma preferência terminológica ainda não tiver sido decidida:

- Não invente o detalhe ausente.
- Registre claramente a pendência.
- Proponha uma solução acompanhada de justificativa, se houver base para isso.
- Não apresente a proposta como decisão editorial aprovada.

Para conteúdos destinados à publicação, resolva as pendências que afetem o comportamento exigido antes de marcar o trabalho como concluído.

## 11. Critérios de aceitação

Um documento está conforme o PTC quando atende aos itens aplicáveis abaixo:

### Correção

- [ ] Não altera o significado das fontes, fórmulas, APIs ou contratos.
- [ ] Distingue obrigações, recomendações e opções.
- [ ] Informa condições e exceções relevantes.
- [ ] Não converte hipóteses ou observações em garantias.
- [ ] Declara limites de ambiente e portabilidade quando necessários.

### Linguagem

- [ ] Usa português brasileiro natural e direto.
- [ ] Prefere voz ativa e sujeitos identificados.
- [ ] Reduz nominalizações e formalismo desnecessário.
- [ ] Mantém um termo para cada conceito no mesmo contexto.
- [ ] Define termos novos quando necessário.
- [ ] Preserva os termos técnicos ingleses já decididos pelo clube.
- [ ] Não perdeu precisão para encurtar o texto.

### Utilidade

- [ ] O leitor consegue identificar o próximo passo.
- [ ] Entradas, comandos e resultados esperados são distinguíveis.
- [ ] Exemplos e testes são coerentes com o contrato.
- [ ] Referências são contextualizadas e verificáveis.
- [ ] Requisitos do núcleo não estão escondidos nas extensões.

## 12. Verificação automática: uso limitado

Ferramentas automáticas podem apontar **candidatos à revisão**, como:

- Frases muito longas.
- Expressões burocráticas recorrentes.
- Variações terminológicas não justificadas.
- Termos normativos usados de modo inconsistente.
- Referências locais quebradas e blocos de código mal formatados.

**Não use como critérios rígidos de reprovação:** número de palavras por frase, presença de voz passiva, quantidade de termos ingleses ou fórmulas de legibilidade genéricas. Essas métricas não demonstram correção técnica.

Uma mudança automática só deve ser aplicada quando preservar o significado. Contratos, literais de código, citações e nomes oficiais precisam ser protegidos contra substituições globais.

## 13. Manutenção da convenção

Esta convenção deve ser versionada junto à documentação editorial do clube.

Uma alteração relevante deve registrar:

- O problema identificado.
- A redação anterior e a proposta.
- A justificativa técnica ou editorial.
- O impacto em documentos já publicados.
- A decisão aprovada.

Não reescreva todo o acervo a cada mudança de preferência. Priorize atualizações que eliminem ambiguidade, erro ou inconsistência material.

O glossário complementa este documento. Ele não deve repetir integralmente suas regras de redação.

---

## Instrução resumida para agentes

> Escreva os conteúdos do Oxide Club em **Português Técnico Claro (PTC)**. Use frases diretas, voz ativa por padrão, verbos de ação e termos consistentes. Explique conceitos novos sem retirar sua precisão. Preserve os termos técnicos em inglês já aprovados, como *syscalls*, *operadores bitwise*, *disassembly*, *stack*, *lifetime*, *calling conventions*, *object file* e *linking*. Em contratos, diferencie com precisão o que **deve**, **não deve**, **recomenda-se** e **pode** ser feito. Declare condições, resultados esperados, erros e limitações. Não invente fatos, medições ou garantias. Revise o conteúdo primeiro quanto à correção técnica e depois quanto à clareza. Quando uma simplificação ameaçar a precisão, preserve a precisão.
