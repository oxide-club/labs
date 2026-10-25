# Starter Rust de concorrência

Use Rust 2021/std e Python 3. Na raiz do laboratório:

```sh
python3 checks/rust/check.py --compile-only
python3 checks/rust/check.py
```

O primeiro comando compila. O segundo rejeita os TODOs em 15 cenários separados,
com timeout por processo e término de suas threads. Depois da implementação, os
15 cenários devem passar. As seis cargas vêm do mesmo `materials/cases.json` do C.

## Contrato adaptado

Implemente `counter_run`, `BoundedQueue` e `ordered` em `concurrency.rs`.
`counter_run` retorna o total em `Ok(u64)` após join, com os limites do enunciado.
Use `Mutex<u64>` no modo Mutex e `AtomicU64` no modo Atomic. Escolha e justifique
`Ordering`. Não substitua incrementos pelo produto nem use estado global.
Limites inválidos retornam `RunError::Invalid`; falha de criação retorna `Spawn`
somente depois de reunir threads já criadas. Panic de worker retorna `Panicked`
depois de reunir os demais. Use `thread::Builder::spawn` para observar falhas.

`new` aceita capacidade 1..64 ou retorna `QueueError::Invalid`.
`push` bloqueia enquanto aberta/cheia e retorna `Closed` após fechamento.
`pop` bloqueia enquanto aberta/vazia, retorna `Some(id)` em ordem FIFO e `None`
somente quando fechada/vazia. `close` é idempotente, preserva itens e desperta
produtores e consumidores. Mutex poisoned retorna `Poisoned`, nunca EOF normal.
Não provoque panic deliberado enquanto segura o lock; recuperação de poison está
fora do exercício. IDs incluem zero e u64::MAX.

Use buffer próprio, mutex e duas condition variables. Não use canal pronto,
fila concorrente pronta, espera ocupada ou sleep como sincronização. `Arc` pode
compartilhar ownership; ele não sincroniza sozinho os campos mutáveis. Os canais
no harness são instrumentação do teste, não implementação da fila.

`ordered` cria duas threads que adquirem os mesmos dois mutexes na mesma ordem,
libera os locks e reúne ambas; retorna os erros de criação/panic como o contador.
Analise também o ciclo do cenário defeituoso em `experiments/deadlock.c` e o modelo
de interleavings. Não reproduza uma data race com `unsafe` para cumprir esta variante.

## Diferenças para C

`Result`, `Option` e `Drop` substituem errno, saída por ponteiro e destruição
manual. O último ownership da fila só deve ser liberado após reunir os usuários.
Nulos, modo inteiro desconhecido e rollback de primitivas pthread não pertencem
à API Rust tipada. Os testes C correspondentes continuam obrigatórios em C.
Falha de criação e poison exigem revisão adicional: os checks públicos não
injetam esses erros. Resultado correto não prova incrementos reais nem uso de
condition variables; revise o código e explique predicados/spurious wakeups.

Rust seguro impede a data race do exemplo C, mas permite erros lógicos, deadlock
e perda de wakeup. As janelas de observação dos testes não provam que uma thread
entrou em espera; a revisão dos invariantes complementa os testes finitos.
O material C permanece nos caminhos históricos em `materials/starter/`.
