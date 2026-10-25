# Guia local — ABI e Calling Conventions

Leia [o enunciado](index.md). Os comandos partem deste diretório, em Linux x86-64:

```sh
python3 checks/check.py
CC=clang python3 checks/check.py
```

O starter compila, mas os checks retornam status 1: faltam cálculo e chamada ao probe.
Essa falha é esperada. O check compila em diretório temporário e remove seus artefatos.
Não há dependências Python externas. O timeout de execução é cinco segundos.
Leia [os materiais](materials/README.md) e siga [o experimento](experiments/calling.md).
Registre evidências no [modelo de relato](report-template.md), incluído a partir do modelo central.

Documentação original: CC BY 4.0. Código original: MIT. Fixtures originais: CC0 1.0.
Fontes externas mantêm suas licenças; não foram copiadas para o laboratório.

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
