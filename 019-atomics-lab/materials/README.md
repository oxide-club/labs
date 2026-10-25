# Materiais — Atomics e memory ordering

## Inventário e responsabilidades

| Arquivo | Uso |
| --- | --- |
| `starter/Cargo.toml` | Crate Rust 2021 e seleção `std`/Loom 0.7.2. |
| `starter/Cargo.lock.txt` | Lock integral, restaurado em cópia pelo runner; formato aceito pelo pacote. |
| `starter/src/lib.rs` | Tipos compartilhados e métodos incompletos do participante. |
| `../checks/public.rs` | Fixtures sequenciais, observações individuais e totais do modelo e amostragem local. |
| `../checks/check.py` | Build e execução isolados, classificação e captura dos diagnósticos. |
| `../checks/test_support.py` | Controles de vacuidade, resumo incoerente, interrupção, panic genérico e teste ausente. |

O `Cargo.lock` histórico no checkout não é necessário na distribuição.
O clube fornece os instrumentos. O participante implementa as operações e explica suas evidências.
Não há solução completa nem argumento de happens-before pronto no pacote.

## Condições verificadas

As fixtures vêm do contrato: estado inicial `None`; leitura sequencial após publicação `Some(42)`.
Esses valores não dependem de uma execução concorrente.
A referência privada foi confrontada com os checks e cinco variantes que violam requisitos distintos.
Os registros da preparação ficam fora da distribuição do participante.
Leia [comandos, limites e estados](../README.md) antes de executar.

## Origem e licenças

Material autoral Oxide Club, revisão de preparação `2026-10-25.2`.
Fonte curricular: atividade 26 do caderno revisado de 25/10/2026.
Código MIT; documentação CC BY 4.0; fixtures CC0 1.0.
Os textos das licenças estão em `licenses/` neste diretório.
Loom 0.7.2: MIT, obtido pelo Cargo, não incorporado ao pacote.
O lock registra origem, versões e checksums das dependências; não contém seus fontes.
