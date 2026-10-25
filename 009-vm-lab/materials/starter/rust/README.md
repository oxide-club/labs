# Starter Rust de VM

Implemente `run(&str, i64) -> Result<State, InvalidBudget>` em `vm.rs`.
Use Rust 2021/std, sem crates. O adaptador `main.rs` apenas transporta o resultado.
Estado, PC, stack, dispatch, parser e validação são trabalho do participante.

Na raiz do laboratório:

```sh
rustc --edition=2021 -D warnings materials/starter/rust/main.rs -o /tmp/oxide-vm-rust
rustc --edition=2021 --test materials/starter/rust/main.rs -o /tmp/oxide-vm-transport
/tmp/oxide-vm-transport
python3 checks/check.py /tmp/oxide-vm-rust
```

Build e teste do transporte devem passar. O check da VM deve rejeitar o TODO.
Após implementar, os mesmos fixtures, estados, traces e fronteiras da API Python
devem passar. Sem argumento, `checks/check.py` continua testando `materials/vm.py`.

## Adaptação da interface

Um executável de outra linguagem recebe **um argumento budget**, a fonte UTF-8
em stdin e emite exatamente um objeto JSON de estado em stdout. Um estado de erro
da VM também usa status de processo zero. Budget inválido usa status 2; defeito
interno usa outro status não zero. Stderr serve para diagnósticos, não para estado.
Cada invocação começa do estado inicial. Timeout do check é cinco segundos.

Na API Rust, budget fora de 1..10000 retorna `Err(InvalidBudget)`; fonte inválida
retorna `Ok(State)` com `invalid_program`. Tipos não inteiros são rejeitados pelo
adaptador antes da API tipada. O domínio de programas continua textual, inclusive
regras de LF/CRLF e ASCII. O limite é de caracteres, não bytes UTF-8: use essa
distinção ao validar uma fonte com caracteres não ASCII.

Use `i32` e operações verificadas: overflow é erro terminal, nunca wrapping ou
panic. Copie a stack para o trace antes da tentativa; `Vec` pode armazenar dados,
mas não deve esconder o ciclo de interpretação nem permitir ultrapassar 32 itens.
Não delegue execução a `eval`, outra VM ou gerador de interpretador.
