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

## Interface Make

Execute da raiz deste laboratório, com GNU Make e Python 3.10+:

```sh
make help                 # Comandos, requisitos e seletores
make setup                # Verifica as ferramentas; não instala globalmente
make build                # Compila sem executar o exercício
make test                 # Checks da solução; o starter pode falhar
make run                  # Experimento padrão
make verify-preparation   # Verifica a preparação do starter original
make clean                # Limpa artefatos conhecidos; preserva resultados
```

`make` sem argumentos mostra ajuda. Veja os seletores `VARIANT`, `MODE` e
`EXPERIMENT` disponíveis em `make help`. Cada pacote funciona independentemente.
A interface exige Linux; requisitos de arquitetura seguem o roteiro acima.
Saídas de `run` ficam em um diretório novo de `results/`; falhas continuam visíveis.
Após modificar o starter, use `test`: `verify-preparation` compara a preparação
original e não comprova a correção da sua solução.

### Experimento e seletores deste laboratório

`make build` compila os harnesses Rust sem executá-los. `make run` acompanha
a execução assíncrona e `make test` verifica o executor. Ambos podem rejeitar
o starter enquanto o executor estiver incompleto.
