# Leituras orientadas — Execução Assíncrona

Consultadas em 25/10/2026. Leia a API primeiro e compare código real depois de
implementar e explicar seu próprio executor. As referências não mudam o contrato.

## Especificação e preparação

- [Rust — Future](https://doc.rust-lang.org/std/future/trait.Future.html): confira
  `Pending`, registro do Waker e a restrição de não consultar novamente após
  `Ready`. Pergunta: um wake garante que a próxima consulta retornará `Ready`?
- [Rust — Wake](https://doc.rust-lang.org/std/task/trait.Wake.html): alternativa
  segura para construir Waker com `Arc`. Pergunta: quais dados precisam aceitar
  acesso de outra thread quando as futures continuam locais?
- [Async Book — Build an Executor](https://rust-lang.github.io/async-book/02_execution/04_executor.html):
  introduz a relação entre fila, tarefa, poll e notificação. O exemplo usa
  `futures::task::ArcWake`; aqui use `std::task::Wake` e não adicione um runtime.
  Compare os contratos antes de copiar decisões de capacidade ou término.

As páginas de std consultadas exibiam Rust 1.99.1; a preparação local usou 1.98.1.
Registre a toolchain usada e consulte também sua documentação instalada.

## Código real: futures-rs

Arquivo: `futures-executor/src/local_pool.rs`, release 0.3.31.
[Fonte consultada na tag](https://raw.githubusercontent.com/rust-lang/futures-rs/0.3.31/futures-executor/src/local_pool.rs).
[Revisão fixa](https://github.com/rust-lang/futures-rs/blob/1e052816b09890925cfdfcbe8d390cdaae5e4c38/futures-executor/src/local_pool.rs),
identificada pelo [commit da release](https://github.com/rust-lang/futures-rs/commit/1e052816b09890925cfdfcbe8d390cdaae5e4c38).

O arquivo implementa `LocalPool`, `LocalSpawner` e a espera de `run_executor`.
Observe `ThreadNotify::wake_by_ref`, o estado `unparked` e a combinação de
`park`/`unpark`. Compare o significado de `run`, `run_until_stalled` e
`try_run_one`: esta última pode avançar várias tarefas antes de concluir uma;
nosso `step` faz no máximo um poll.

O código real usa `FuturesUnordered`, `ArcWake` e interfaces de spawning mais
amplas. Não deduza dele a ordem FIFO exigida por este exercício.
Pergunta de leitura: por que `Pending` não implica ausência de uma notificação
pendente, e como o sinal continua visível até a espera?

Verificação: a fonte na tag e o commit da release foram acessíveis; o mecanismo
acima foi lido na tag. A ferramenta de consulta retornou `Cache miss` ao abrir
diretamente o arquivo pelo SHA e a API de commits ficou indisponível. Não se
afirma uma segunda verificação do conteúdo por SHA. Nenhum código externo foi
copiado para o pacote; futures-rs declara MIT ou Apache-2.0.
