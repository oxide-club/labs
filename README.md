# Laboratórios do Oxide Club

Investigações em que a entrega reúne evidências, explicação e código.
Cada diretório numerado contém um roteiro em `index.md`, materiais e verificações.
O site consome esta fonte; não edite o checkout gerado `.content/labs`.

## Catálogo

- 005 — Laboratório de Cache e Localidade: disponível neste repositório.

## Nomes reservados

- 001 — Laboratório de Representação Binária
- 002 — Laboratório de Engenharia Reversa
- 003 — Laboratório de Segurança de Memória
- 004 — Laboratório de Alocação de Memória
- 006 — Laboratório de Processos e Pipes

Os números são identificadores, não uma sequência obrigatória.

## Verificação editorial

Execute `python3 -m unittest discover -s tests` e
`python3 scripts/verify-cache-model.py`. O modelo independente é uma ferramenta
de revisão dos vetores, não parte do pacote inicial do participante.

Consulte [contribuição](CONTRIBUTING.md) e [licenças](LICENSING.md).
