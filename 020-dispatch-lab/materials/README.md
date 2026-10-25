# Materiais — Monomorfização e dynamic dispatch

| Arquivo | Responsabilidade |
| --- | --- |
| `starter/rust/Cargo.toml` | Workspace e perfis comparáveis O0/O3. |
| `starter/rust/Cargo.lock.txt` | Lock distribuível, restaurado pelo runner. |
| `starter/rust/core/Cargo.toml` e `core/src/lib.rs` | API e cinco corpos incompletos do participante. |
| `starter/rust/harness/Cargo.toml` e `harness/src/main.rs` | Loader, validação agregada, aquecimento e medição fornecidos pelo clube. |
| `generate.py` | Dataset por fórmula de índice e oráculo em inteiros ilimitados. |
| `fixtures/small.json` | Vetores vazios, overflow e repetições, calculados independentemente. |
| `../checks/public.rs` | Checks de API, parâmetros, ordem e quantidade de chamadas. |
| `../checks/check.py` e `test_support.py` | Build isolado, equivalência e conferência dos instrumentos. |
| `../experiments/collect.py` e `summarize.py` | Coleta real, inspeção, dados brutos e dispersão. |

O participante implementa `Add::apply`, `Mul::apply`, `generic`, `dynamic` e `enumerated`.
O clube fornece preparação e coleta; nenhuma tabela de desempenho é entregue como resposta.
A referência privada e cinco mutantes ficam fora da distribuição.
O `Cargo.lock` gerado localmente não é necessário no pacote.

O dataset usa `((i * 0x9e3779b97f4a7c15) ^ 0xd1b54a32d192ed03) mod 2^64`.
A geração ocorre antes da medição e registra o tamanho escolhido.
Os resultados esperados são calculados por soma matemática ilimitada, seguida de módulo.
O check independente também reduz cada elemento antes de acumular.
Veja [comandos e limites](../README.md).

## Linguagens e ambiente

Rust é obrigatório no núcleo. Linux x86-64, Rust/Cargo 1.98.1 e GNU binutils.
Os instrumentos isolam a configuração Cargo e registram as flags efetivas; consulte o guia local.
Não alteram afinidade, governor ou políticas do host.

## Origem e licenças

Materiais autorais Oxide Club, revisão `2026-10-25.2`, baseados na atividade curricular 27.
Código MIT; documentação CC BY 4.0; dados e fixtures CC0 1.0.
Os textos das licenças estão em `licenses/` neste diretório.
Não há código externo nem dependências de terceiros incorporadas.
