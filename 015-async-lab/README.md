# Guia local — Execução Assíncrona

Leia [o enunciado](index.md) antes de alterar os starters.
Use Rust estável, edição 2021, e Python 3.10+. Os comandos abaixo partem deste
diretório e não exigem crates externos:

```sh
python3 checks/check.py --compile-only
python3 checks/check.py --fixture-only
python3 checks/check.py
python3 experiments/trace.py --compile-only
python3 experiments/trace.py
```

Os comandos `--compile-only` verificam a preparação, e `--fixture-only` testa a
future independente que serve de instrumento aos checks. Todos devem retornar 0.
Os comandos sem opção rejeitam o starter por `todo!`: essa falha é esperada.
Depois de implementar executor e evento, os dez checks no Linux devem passar e o trace
deve concluir. Os runners compilam em diretórios temporários e limitam cada caso
a cinco segundos; timeout é falha, não evidência automática de deadlock.

Veja [os materiais](materials/README.md), [o roteiro do experimento](experiments/README.md)
e [as referências](references.md). Registre previsão, observação, implementação,
invariantes e limites no [modelo de relato](report-template.md), gerado do modelo central.
Não altere os checks para fazer a implementação passar.

Documentação original: CC BY 4.0. Código original: MIT. Dados de teste originais:
CC0 1.0. Fontes externas conservam suas próprias licenças.
