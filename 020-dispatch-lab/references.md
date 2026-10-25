# Referências orientadas — Monomorfização e dynamic dispatch

- **R27.1 — [Rust Reference: Trait objects](https://doc.rust-lang.org/reference/types/trait-object.html).** Ler a seleção de métodos e o papel da vtable.
- **R27.2 — [rustc-dev-guide: Monomorphization](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html).** Identificar coleta de instâncias e codegen units.
- **R27.3 — [`black_box`](https://doc.rust-lang.org/std/hint/fn.black_box.html).** Ler as limitações e os exemplos de trabalho eliminado pelo otimizador.
- **R27.4 — [Código real: `rustc_codegen_ssa/mir/block.rs`](https://github.com/rust-lang/rust/blob/1.98.1/compiler/rustc_codegen_ssa/src/mir/block.rs).** Localizar o tratamento de `InstanceKind::Virtual` na preparação de chamadas; seguir de onde vêm o receptor e a função invocada. São detalhes internos sujeitos a mudança.

## Revisões consultadas

Consulta em 25/10/2026: Rust Reference, capítulo Monomorphization do rustc-dev-guide
 e documentação de `black_box` (página móvel apresentando Rust 1.99.1).
O compilador validado é Rust 1.98.1, commit `48a229ceaefd4985c50990b14116b6d856af0985`.
Não confunda uma página móvel com o código exato desse build.
O link web versionado de `black_box` em 1.98.1 não ficou acessível nesta consulta.

O arquivo de codegen prepara chamadas virtuais de programas gerais; o laboratório compara apenas operações homogêneas.
Localize `InstanceKind::Virtual` e acompanhe a obtenção da função e do receptor.
Explique por que esse ramo do compilador não garante uma chamada indireta sobrevivente após as otimizações.

O fonte nightly de `block.rs` foi consultado; a página contém a revisão
`12433c307b5a497388ffe2f4e49dbf1ab8c71fa0`. A tentativa de consultar a tag 1.98.1
nesse caminho falhou. Essa leitura é contextual e não representa o código exato do build medido.

## Correção da consulta — resposta à revisão

Em 25/10/2026, a consulta direta ao fonte bruto da tag 1.98.1 funcionou:
[block.rs, Rust 1.98.1](https://raw.githubusercontent.com/rust-lang/rust/1.98.1/compiler/rustc_codegen_ssa/src/mir/block.rs).
O arquivo contém `InstanceKind::Virtual`, inclusive na preparação da chamada.
SHA-256: `13d6d31caf4c1693ec26c4fa4d8385361d816413b1c9fbc77a71b914face653b`.
O registro anterior de falha permanece como histórico da ferramenta de consulta.
Ele não demonstra indisponibilidade da referência: o acesso direto autorizado respondeu nesta revisão.
Os links R27.4 agora apontam para a tag correspondente ao compilador validado.
