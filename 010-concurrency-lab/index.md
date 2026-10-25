---
title: Laboratório de Concorrência e Sincronização
area: systems-concurrency
slug: 010-concurrency-lab
summary: Corrija um contador, implemente uma fila limitada e investigue deadlock.
question: Como coordenar threads que compartilham estado e precisam terminar?
draft: false
publishedAt: 2026-10-25
topics: [Concorrência, Sincronização]
prerequisites: [C, Structs, Memória compartilhada, Threads]
tools: [Compilador C11, pthreads, Python 3]
environment: Linux com pthreads e Python 3.10 ou superior
difficulty: intermediate
---

## O que vamos investigar

Concorrência permite progresso por interleavings; paralelismo envolve execução simultânea.
Uma data race envolve acessos conflitantes ao mesmo objeto, sem a sincronização exigida pela linguagem, com pelo menos uma escrita.
Em C, uma data race produz comportamento indefinido (UB). O resultado do contador defeituoso não tem faixa nem valor garantidos.
Uma race condition é um defeito que depende da ordem de eventos; pode existir mesmo sem data race.
Um deadlock ocorre quando threads esperam indefinidamente por recursos que não podem obter.

### Contrato técnico

Implemente as interfaces em [counter.h](materials/starter/counter.h) e [queue.h](materials/starter/queue.h), usando C11 e pthreads.
O contador oferece modos `COUNTER_UNSAFE`, `COUNTER_MUTEX` e `COUNTER_ATOMIC`.
`counter_run(mode, threads, iterations, out)` aceita 1..32 threads e 0..1000000 incrementos por thread.
Os modos mutex e atomic devem retornar zero e gravar `threads * iterations` em `*out`, após reunir todas as threads.
Use mutex na primeira variante e operações C11 sobre objeto atômico na segunda. Não substitua os incrementos pelo produto.
O modo unsafe fornecido existe somente para diagnóstico; não se exige resultado numérico específico.
Modo desconhecido, ponteiro out nulo ou limites inválidos retornam `EINVAL`, preservando saída não nula.
Falha de inicialização/criação retorna o código pthread, reúne threads já criadas e preserva a saída.
Chamadas independentes não compartilham contadores. Não use `volatile` como sincronização.

A fila guarda IDs `uint64_t`, inclusive zero e UINT64_MAX. Capacidade válida: 1..64 itens.
O chamador fornece uma `Queue` cujo endereço permanece válido até `queue_destroy` e não a copia depois de inicializada.
Os campos expostos no header são espaço de implementação, não API de observação concorrente.
Somente `queue_init` pode receber uma fila não inicializada. Não chame init duas vezes sem destroy.

| Operação | Resultado obrigatório |
| --- | --- |
| queue_init(q, capacity) | Retorna 0, cria fila aberta/vazia. Nulo ou capacidade inválida: EINVAL. Falha pthread: código recebido, desfaz inicialização parcial; não usar nem destruir essa fila. |
| queue_push(q, id) | Aguarda enquanto aberta e cheia. Insere exatamente um ID e retorna 0; se fechada, retorna EPIPE sem inserir. |
| queue_pop(q, out) | Aguarda enquanto aberta e vazia. Retira o item mais antigo e retorna 0; se fechada e vazia, retorna ENODATA preservando out. |
| queue_close(q) | Retorna 0, fecha de modo idempotente e desperta produtores e consumidores em espera. Não descarta itens. |
| queue_destroy(q) | Retorna 0 e libera primitivas; exige fila fechada e todas as operações concluídas/threads reunidas. |

Nas operações após init, q nulo ou out nulo em pop retorna EINVAL antes de acessar a fila.
Nos demais casos, são pré-condições: fila inicializada, uso conforme lifetime e ausência de cancelamento de threads.
Erros de primitivas pthread durante operações sobre fila válida estão fora do modelo do exercício; não esconda erros de programação como encerramento normal.
O resultado de push concorrente com close depende de qual operação se efetiva primeiro: inserção completa ou EPIPE.
A fila deve preservar FIFO na ordem em que inserções se efetivam, sem perder nem duplicar IDs.
A ordem de retornos ou de prints de consumidores não define a ordem de retirada.
Depois de close, consumidores devem drenar itens existentes e receber ENODATA. Nenhuma thread pode ficar presa por falta de notificação.
Não há requisito de justiça entre threads. Pressupõe-se que threads executáveis recebam tempo de CPU.

Use mutex e variáveis de condição na fila; espera ocupada e delays como sincronização não atendem ao contrato.
Documente qual lock protege buffer, índices, quantidade e estado de fechamento.
Explique os invariantes `0 <= count <= capacity`, os predicados de espera e o efeito de notificações e spurious wakeups.
O coordenador deve reunir produtores antes de fechar a fila e reunir consumidores antes de destruí-la.
Os checks também fecham com operações pendentes para investigar o protocolo de wakeup.

O programa de deadlock possui modos `bad` e `ordered`. O primeiro fornece duas aquisições em ordem oposta e uma barrier que estabelece o ciclo.
Complete `ordered`: ambas as threads devem adquirir os dois locks na mesma ordem global, liberá-los e terminar com status 0 e `completed`.
Não mantenha entre aquisições a barrier do cenário defeituoso: uma thread poderia esperar na barrier enquanto a outra espera seu lock.
O modo incompleto retorna 77. Os scripts limitam cada processo e encerram somente o processo que criaram, executando seu reaping.

## Antes de começar

### Linguagens e ambiente

Referência: **C11**. Aceitas: Livre sob contrato de sincronização; por exemplo C, Rust, C++ e Go.
Recomendadas: Rust, C++ e Go. Mutex, atomics e condition variables; fila limitada própria; sem canal pronto no mecanismo.
Materiais oficiais: C11 existente; Rust: `materials/starter/rust/`.
Equivalência: equivalente sob contrato adaptado.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

Conheça funções, structs, lifetime e criação/reunião de threads. Leia [o guia local](README.md).
Use compilador C11, pthreads, linker com `--wrap` e Python 3.10+. ThreadSanitizer é opcional; registre indisponibilidade ou falha do runtime.

## Materiais

[O guia de materiais](materials/README.md) identifica starters, fixtures e programas completos de diagnóstico.
[Os checks públicos](checks/check.py) compilam em diretório temporário e verificam cada cenário com timeout.
[O roteiro de experimentos](experiments/README.md) separa previsão, observação e explicação.

## Etapas da investigação

1. **Prever:** decomponha dois incrementos em leituras/escritas num modelo de interleavings e desenhe o ciclo de espera entre locks. Esse modelo não especifica o comportamento C com UB.
2. **Observar:** execute o modelo, o contador unsafe e o cenário bad pelos scripts com timeout. Registre comando, saída e diagnóstico sem exigir que o contador erre.
3. **Explicar:** escreva uma tabela de campos protegidos, invariantes, predicados de espera e eventos de wakeup. Diferencie exclusão mútua de progresso.
4. **Implementar:** complete contador mutex/atomic, fila e modo ordered. Justifique a ordem de memória escolhida para o contador.
5. **Verificar:** execute os checks. Compare IDs individualmente, explique fechamento com fila cheia/vazia e registre término das threads. Execute TSan se disponível.

## Critérios de conclusão

Os checks devem retornar zero após implementação. Entregue código, tabela de invariantes, comparação mutex/atomics e análise do deadlock.
Inclua pelo menos uma previsão revisada após observar dados. Registre ambiente, flags e limitações das ferramentas.
Repetições bem-sucedidas não provam ausência de deadlocks ou data races; justifique também acesso, visibilidade e progresso pelos invariantes.

## Extensões opcionais

Meça contenção somente após verificar correção. Registre repetições e use relógio monotônico.
Investigue false sharing, ordens de memória ou starvation, distinguindo observação de garantia de justiça.
Uma fila lock-free é um projeto separado, não requisito deste núcleo.

## Participação no clube

Compartilhe uma tentativa com entrada mínima, previsão e saída observada. Use [o modelo de relato](report-template.md).
Ao revisar, identifique o invariante ou ciclo de espera que sustenta sua conclusão.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md) depois de formular os invariantes da fila.
Relacione fechamento ao EOF de pipes e notificações ao progresso de executores assíncronos.
