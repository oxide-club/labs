# Guia local — Multiplicação Matricial

Leia [o enunciado](index.md) e [o contrato](materials/README.md).
Use Linux, GCC ou Clang C11, Python 3 e uma CPU com double binary64.

## Preparar e verificar

A partir deste diretório, execute:

```sh
cc --version
python3 --version
python3 checks/check.py
cc -std=c11 -O2 -Wall -Wextra -Wpedantic -I materials/starter -I checks experiments/benchmark.c materials/starter/matrix.c -lm -o /tmp/matrix-benchmark
```

Edite `materials/starter/matrix.c`. O starter compila, mas o check retorna 1 e o benchmark
recusa medir porque as três funções retornam MATRIX_TODO. Isso é uma falha esperada.
Após implementar, o check deve retornar 0. Para investigar memória, compile também com
`-O1 -g -fsanitize=address,undefined`; não use essa compilação para comparar tempos.

## Medir e registrar

Siga [o roteiro](experiments/README.md). Use [o modelo de relato](report-template.md).
Entregue código, saída dos checks, CSV bruto, resumo por variante, versões e hipótese original.

## Licenças

Documentação original: CC BY 4.0. Código original: MIT. Dados originais: CC0 1.0.
Os avisos completos constam no pacote e no repositório; fontes OpenBLAS são somente links.

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
