# Laboratórios do Oxide Club

Cada laboratório propõe uma investigação. A entrega inclui código, resultados observados e uma explicação.
Cada diretório numerado contém um roteiro em `index.md`, materiais e verificações.
O site lê os arquivos deste repositório.
Não edite a cópia gerada em `.content/labs`.

## Catálogo

- 005 — Laboratório de Cache e Localidade: disponível neste repositório.

## Nomes reservados

- 001 — Laboratório de Representação Binária
- 002 — Laboratório de Engenharia Reversa
- 003 — Laboratório de Segurança de Memória
- 004 — Laboratório de Alocação de Memória
- 006 — Laboratório de Processos e Pipes

Os números identificam os laboratórios. Você pode escolher a ordem de estudo.

## Verificação editorial

1. Execute `python3 -m unittest discover -s tests`.
2. Execute `python3 scripts/verify-cache-model.py`.

O modelo independente verifica os resultados esperados dos experimentos.
O pacote do participante não inclui esse modelo.

Consulte [contribuição](CONTRIBUTING.md) e [licenças](LICENSING.md).
