# Referências orientadas — Atomics e memory ordering

- **R26.1 — [`Ordering`](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html).** Ler as restrições de operação e a condição de sincronização entre Release e Acquire.
- **R26.2 — [Loom: documentação oficial da crate](https://docs.rs/loom/0.7.2/loom/).** Ler Writing tests e Limitations and Caveats, especialmente Relaxed Memory Ordering.
- **R26.3 — [Código real: `core/sync/atomic.rs`](https://github.com/rust-lang/rust/blob/1.98.1/library/core/src/sync/atomic.rs).** Localizar `atomic_load` e `atomic_store`; comparar o encaminhamento a intrinsics e as ordenações recusadas. Não usar os intrinsics privados no laboratório.

## Revisões consultadas

Consulta em 25/10/2026: Loom 0.7.2, incluindo os campos do
[Builder](https://docs.rs/loom/0.7.2/loom/model/struct.Builder.html).
A documentação móvel de Ordering apresentou Rust 1.99.1; o build validado usa Rust 1.98.1.
A documentação instalada de 1.98.1 permite conferir a versão correspondente com `rustup doc --std`.
O código real de `atomic.rs` encaminha operações aos intrinsics e rejeita ordenações incompatíveis.
Compare as pré-condições desse código geral com o protocolo one-shot do laboratório.
Não copie intrinsics privados para o experimento.

Os links web versionados de std 1.98.1 não ficaram acessíveis nesta consulta.
Não se declara identidade entre a documentação móvel e o compilador validado.

O fonte `atomic.rs` da release Rust 1.98.1 foi consultado no repositório oficial.
