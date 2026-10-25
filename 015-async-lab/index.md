---
title: Laboratório de Execução Assíncrona
slug: 015-async-lab
summary: Construa um executor cooperativo com notificações e estados explícitos.
question: Como várias tarefas progridem sem uma thread para cada tarefa?
draft: false
publishedAt: 2026-10-25
topics: [Rust, Futures, Concorrência]
prerequisites: [Ownership, Traits, Filas, Concorrência básica]
tools: [Rust, Python 3]
environment: Linux com Rust estável e Python 3.10 ou superior
difficulty: advanced
---

## O que vamos investigar

Uma future representa uma computação que pode estar pendente. O executor chama
`Future::poll` com um `Context`; o resultado é `Poll::Pending` ou `Poll::Ready(())`.
O `Waker` guardado pela tarefa solicita outra oportunidade de execução.
Notificar não significa chamar `poll` imediatamente nem concluir a tarefa.
Construa um executor single-threaded, sem runtime externo, usando somente Rust std.

### Contrato técnico

Implemente estas interfaces em `materials/executor.rs`:

```rust
pub type TaskId = usize;
pub enum Step { Polled { id: TaskId, ready: bool }, Idle, Complete }
pub struct Executor { /* estado privado */ }
impl Executor {
    pub fn new() -> Self;
    pub fn spawn<F: Future<Output = ()> + 'static>(&mut self, future: F) -> TaskId;
    pub fn step(&mut self) -> Step;
    pub fn run(&mut self);
    pub fn active(&self) -> usize;
}
```

`Step` deve implementar `Debug`, `PartialEq` e `Eq`. `new` começa vazio.
`spawn` guarda a future sem executar `poll`, atribui IDs consecutivos desde zero
e coloca a tarefa no fim da fila pronta. IDs nunca são reutilizados.
O domínio do exercício tem menos de `usize::MAX` tarefas por executor e memória
suficiente; esgotamento de IDs ou allocation fica fora do contrato.
Futures não precisam implementar `Send` ou `Unpin`: mantenha-as locais e fixadas
com `Pin`, por exemplo `Pin<Box<dyn Future<Output = ()>>>`.

`step` não espera um evento: executa no máximo um `poll` da primeira tarefa pronta.
Retorna `Polled` com o ID e `ready` igual ao resultado desse poll. Sem tarefa pronta,
retorna `Idle` se ainda há tarefas pendentes, ou `Complete` se todas terminaram.
`active` conta tarefas que ainda não retornaram `Ready`, inclusive as prontas.
`Ready` remove e libera a future antes de `step` retornar; nunca volte a consultá-la.

Uma notificação de tarefa viva coloca seu ID no fim da fila. Notificações repetidas
antes de retirar esse ID para o próximo poll devem se fundir em uma entrada.
Uma notificação durante `poll`, seguida de `Pending`, garante outra oportunidade.
Se esse poll retorna `Ready`, descarte também qualquer notificação residual.
Notificar uma tarefa concluída ou um executor destruído deve ser seguro e não
executar nada. O `Waker` pode ser clonado, consumido por `wake` e acionado por outra
thread. Só a thread que chama `step` ou `run` executa as futures; a API não precisa
permitir mover o executor entre threads.

`run` aplica a mesma ordem FIFO até `active() == 0`. Quando há tarefas pendentes e
a fila está vazia, deve esperar uma notificação com uma primitiva blocking, sem
busy-loop, polling periódico ou `sleep` como política de agendamento.
Não retorne por a fila estar momentaneamente vazia nem espere que todos os clones
de Waker sejam destruídos para terminar. Se ninguém notificar uma tarefa pendente,
`run` pode esperar indefinidamente. Os testes têm timeout externo para esse caso.
Depois de terminar, o executor aceita novos `spawn` e novas chamadas a `run`.

`poll` deve retornar em tempo finito. Uma tarefa que bloqueia ou se notifica
indefinidamente pode impedir a conclusão global; a fila FIFO evita que a tarefa
sempre pronta ultrapasse tarefas já enfileiradas. Panics de futures podem propagar;
recuperação do executor após panic, cancelamento explícito, I/O e timers não integram
o núcleo. Destruir o executor descarta as futures restantes sem executá-las.

Implemente também `materials/event.rs`: `event() -> (Event, Signal)` cria um evento
de uso único, inicialmente não sinalizado. `Event: Future<Output = ()>` retorna
`Pending` até `Signal::signal(&self)` marcar o evento. `Signal: Clone + Send + Sync`.
O sinal é persistente, inclusive antes do primeiro poll; repetições são idempotentes.
Um poll pendente registra o Waker mais recente. A primeira sinalização acorda esse
Waker, se houver; não perca um sinal concorrente com o registro. Não segure um lock
ao chamar código de wake externo. Destruir Signal sem sinalizar não conclui Event.
Sinalizar após destruir ou concluir Event é seguro. Não faça poll após `Ready`.

Use `Wake` com `Arc` para construir Wakers seguros. Explique a separação entre
o estado local das futures e o estado compartilhável das notificações.
O núcleo não precisa de `unsafe` nem `RawWaker`.

## Antes de começar

### Linguagens e ambiente

Referência: **Rust**. Aceitas: Rust para Future/Poll/Waker; C e C++20 como comparações de outro modelo.
Recomendadas: Rust; C++20 para comparação. Rust 2021/std; executor single-threaded próprio; sem Tokio ou runtime pronto.
Materiais oficiais: Rust existente.
Equivalência: apenas comparativa entre modelos; Rust é o núcleo atual.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
A restrição preserva o mecanismo observado no núcleo.

Conheça traits, ownership, `Rc`, `Arc`, `Mutex` e o propósito de `Pin`.
Este laboratório pressupõe Rust; não é uma introdução à linguagem.
Instale Rust estável com suporte à edição 2021 e Python 3.10+.
Os materiais não baixam crates e não precisam de Cargo ou rede para executar.
Registre `rustc --version`, `python3 --version` e o sistema no relato.

## Materiais

Leia [o guia local](README.md) e [o mapa dos materiais](materials/README.md).
Os starters de executor e evento compilam, mas contêm `todo!`.
[Os checks](checks/public.rs) usam futures próprias para verificar o executor,
sem depender do evento que você deve implementar.
[O experimento](experiments/README.md) registra chamadas e resultados de poll.
Use [o modelo de relato](report-template.md), gerado do modelo compartilhado.

## Etapas da investigação

1. **Prever:** leia `experiments/trace.rs` e anote a ordem dos IDs, dos resultados
   e da sinalização, antes de executar. Identifique onde pode haver `Idle`.
2. **Observar:** execute `python3 checks/check.py --compile-only`. O starter deve
   compilar. Execute sem a opção e registre a rejeição por `todo!`, sem tratá-la
   como conclusão da investigação.
3. **Explicar:** desenhe os estados pronta, em poll, pendente e concluída.
   Explique onde se registra a notificação que ocorre durante poll e como o
   executor distingue fila vazia de ausência de tarefas vivas.
4. **Implementar:** complete executor e evento. Preserve a API e a ordem definida.
   Justifique a sincronização entre publicar estado, registrar Waker e esperar.
5. **Verificar:** execute `python3 checks/check.py` e
   `python3 experiments/trace.py`. Compare o trace observado à previsão.
   Explique por que uma tarefa sem sinal não recebe novos polls e por que `run`
   realmente bloqueia: os checks de contagem não detectam todo loop interno vazio.

## Critérios de conclusão

- Todos os checks passam, inclusive wake durante poll, duplicação, wake tardio,
  notificação por thread, duas tarefas cooperativas e futures sem `Send`.
- O trace identifica tarefa, resultado e evento; previsão e observação permanecem separadas.
- O código usa espera blocking sem polling periódico. A revisão explica por que
  não há perda de sinal na transição entre observar a fila vazia e esperar.
- O relato justifica coalescing, liberação ao concluir, ausência de ciclos de
  referências que mantenham futures vivas e limites de progresso cooperativo.
- A explicação reconhece que testes finitos não provam ausência de todas as races.

## Extensões opcionais

Acrescente cancelamento com contrato explícito, timer que não bloqueie `poll` ou
driver de I/O. Só depois considere múltiplos workers: isso muda as exigências de
ownership, `Send`, sincronização e progresso. Não substitua o executor por Tokio.

## Participação no clube

Compartilhe previsão, trace, comandos e uma dúvida específica sobre os invariantes.
Uma tentativa parcial deve indicar quais checks ainda falham. Não publique uma
solução completa como parte dos materiais iniciais do laboratório.

## Referências e atividades relacionadas

Consulte [as leituras orientadas](references.md) depois de formular os invariantes.
Máquinas virtuais e concorrência ajudam a entender estados e sincronização.
O número 015 identifica este pacote; a atividade corresponde à seção curricular 13.

Na verificação Linux, execute também o check de CPU/esperas de `checks/check.py`; registre o resultado e explique a primitiva blocking e o predicado usados em `run`. Esse diagnóstico tem limites documentados no guia.
