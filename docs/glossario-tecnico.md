# Glossário técnico

Este glossário complementa o [guia de redação](guia-de-redacao.md).
As formas abaixo seguem o currículo e o PTC fornecidos pelo clube.
Não substitua identificadores, mensagens ou termos citados de especificações externas.

| Forma preferida | Definição e contexto | Evitar como substituição automática |
| --- | --- | --- |
| host | Sistema ou máquina que hospeda a execução ou a VM. Em contraste com device, indica o lado CPU da aplicação GPU. Escolha aprovada pelo responsável. | hospedeiro / hospedeira |
| tail size | Quantidade de elementos restantes quando o tamanho não é múltiplo do bloco ou tile. Por exemplo, 65 elementos e blocos de 64 produzem tail size 1. Escolha aprovada pelo responsável. | tamanho com cauda |
| syscall / syscalls | Interface pela qual um programa solicita um serviço ao kernel. Uma função de biblioteca não é necessariamente uma syscall. | chamada ao sistema |
| operadores bitwise | Operações sobre a representação em bits, como `&`, `\|`, `^` e deslocamentos. | operadores bit a bit |
| disassembly | Representação textual de instruções de máquina decodificadas. Interpretar sua lógica é outra tarefa. | desmontagem |
| stack | Estrutura LIFO de uma máquina abstrata ou região usada na execução de funções; declare o contexto. | pilha em contexto de execução |
| lifetime | Intervalo em que um objeto existe segundo o modelo da linguagem. Um endereço remanescente não prolonga esse intervalo. | tempo de vida como variação estilística |
| calling conventions | Regras de passagem de argumentos, retorno e preservação de estado entre funções. | convenções de chamada |
| object file | Artefato da compilação/montagem com código, dados, símbolos e possíveis relocations. | arquivo objeto |
| linking | Composição de objetos e resolução de referências simbólicas. | ligação |
| static linking | Incorporação de código de objetos ou archives durante o linking. Pode abranger apenas uma biblioteca. | ligação estática |
| dynamic linking | Resolução de dependências entre objetos compartilhados durante carregamento ou execução. | ligação dinâmica |
| dynamic loader | Componente que carrega objetos compartilhados e realiza tarefas de resolução e relocation. | carregador dinâmico |
| buffer | Região usada para armazenar dados durante uma operação. Seu tamanho e sua capacidade podem diferir. | alternar com área temporária sem motivo |
| heap | Contexto usual de armazenamento dinâmico; não implica uma única política de alocação. | stack |
| data race | Acessos conflitantes ao mesmo local de memória sem a sincronização exigida, com pelo menos uma escrita. Em C, causa comportamento indefinido. | race condition como sinônimo exato |
| race condition | Resultado que depende da ordem ou do momento relativo de operações concorrentes. Pode existir sem data race. | data race como sinônimo exato |
| deadlock | Estado em que participantes aguardam recursos ou eventos de modo que não conseguem progredir. | demora como prova de deadlock |
| concorrência | Progresso de mais de uma atividade durante intervalos sobrepostos. | paralelismo como sinônimo |
| paralelismo | Execução simultânea em mais de uma unidade de processamento. | concorrência como sinônimo |
| cache hit / hit | Acesso atendido por um bloco residente e válido no modelo estudado. | acerto quando criar variação desnecessária |
| cache miss / miss | Acesso cujo bloco não está residente e válido na cache estudada. | falta quando criar variação desnecessária |
| eviction | Remoção de um bloco válido para instalar outro. No modelo de cache do clube, também conta como miss. | confundir com todo miss |
| trace | Registro ordenado de eventos ou acessos; declare seu formato. | medir tempo a partir de uma contagem simulada |
| invariante | Propriedade que deve permanecer verdadeira nos estados ou fronteiras definidos pelo contrato. | afirmação sem condições |
| overflow | Resultado que excede a faixa representável; a consequência depende do tipo e do contrato. | tratar todo overflow como wraparound |
| memory mapping | Associação entre uma região de endereços virtuais e um objeto de memória ou arquivo. | equivaler endereço virtual a offset de arquivo |
| ABI | Contrato binário entre componentes, incluindo representação e convenções de chamada. | API como sinônimo |
| API | Interface de programação, com operações e contratos de uso. | ABI como sinônimo |
| seção ELF | Organização lógica dos dados no arquivo, usada por ferramentas de linking e inspeção. | segmento |
| segmento ELF | Descrição de uma região relevante ao carregamento do executável. | seção |
| memory leak | Armazenamento que deixa de ser liberado quando necessário, por perda do acesso ou da responsabilidade por sua liberação. | vazamento de memória |
| borrowing | Acesso a um objeto sem transferir seu ownership; em Rust, referências expressam esse acesso e têm regras de lifetime. | empréstimo |
| reaping | Coleta do status de um processo terminado por seu pai, por exemplo com waitpid. Enviar um sinal não realiza reaping. | recolhimento de processo |
| scheduler | Componente que escolhe quais tarefas executáveis recebem processamento. | escalonador |
| interleaving | Ordem relativa de operações de atividades concorrentes. Um modelo de interleavings não descreve todo comportamento permitido por uma linguagem. | intercalação |
| spurious wakeup | Retorno de uma espera sem garantia de que seu predicado se tornou verdadeiro. | despertar espúrio |
| blocking / non-blocking | Neste catálogo, distingue uma operação que pode esperar um evento externo de outra que retorna sem essa espera. Declare o contrato; não implica automaticamente lock-free. | bloqueante / não bloqueante |
| blocking de matrizes | Divisão de operações em blocos menores para explorar localidade. Neste contexto, não significa esperar um evento externo. | tiling; técnica de blocagem |
| header | Metadados iniciais de uma mensagem ou objeto; em C, também designa um arquivo de declarações. Declare o contexto. | cabeçalho |
| sentinel | Valor ou objeto escolhido para marcar estado ou detectar um comportamento. Sua validade depende do contrato. | sentinela |
| overlap | Interseção entre regiões de armazenamento ou intervalos; declare os limites considerados. | sobreposição |
| barrier | Ponto de sincronização que exige a chegada dos participantes definidos pelo mecanismo. | barreira de sincronização |
| kernel launch | Solicitação de execução de um kernel na GPU; a conclusão pode ocorrer depois do retorno ao host. | lançamento de kernel |
| causal mask | Regra que impede uma posição de attention de usar posições futuras. | máscara causal |
| reduction | Combinação de vários valores em um resultado, como a soma de um vetor. | redução computacional |
| tail | Parte final que não completa um bloco ou tile. Tail size indica quantos elementos ela contém. | cauda |
| allocation / deallocation | Obtenção e liberação de armazenamento. As consequências para objetos e lifetime dependem da linguagem e da API. | alocação / desalocação |
| ownership | Responsabilidade por um recurso, incluindo seu uso e sua liberação conforme o contrato. | posse de recurso |
| file descriptor | Inteiro que identifica uma entrada na tabela de arquivos abertos de um processo. Não é o próprio arquivo. | descritor de arquivo |
| coalescing | Combinação de operações compatíveis; em GPU, aplica-se a acessos de threads atendidos por transações de memória. Declare o contexto. | coalescência |
| offset | Distância em bytes ou posições a partir de uma origem definida. Não substitui deslocamento de bits, que é outra operação. | deslocamento de endereço |

Use ponteiro, registrador, processo, arquivo, endereço, alinhamento e memória virtual em português.
Termos novos devem ser definidos no enunciado quando forem necessários para começar.

## Decisões futuras

Registre termo, alternativas, contexto, justificativa e status proposto/aprovado antes de alterar uma escolha compartilhada.
Não use este glossário como dicionário completo nem como regra de substituição global.

## Decisões do responsável em 25/10/2026

Permanecem em português: memória compartilhada, biblioteca compartilhada, ponteiro,
registrador, endereço, alinhamento, alocador, espera ocupada, variável de condição
e exclusão mútua. Os demais termos aprovados nesta revisão usam as formas inglesas
da tabela. A escolha substitui as propostas anteriores; não há consulta pendente.

A revisão se aplica à prosa autoral e aos comentários. APIs, identificadores,
formatos, mensagens contratuais, exemplos literais e títulos de fontes externas
conservam sua forma quando a mudança afetaria fidelidade ou reprodutibilidade.
Verbos portugueses como liberar e esperar continuam permitidos. Palavras genéricas
não recebem substituição automática: reduzir custo não é executar uma reduction.
