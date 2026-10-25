# Syscalls

Leia [o contrato](index.md) antes de modificar o código.

```sh
make -C materials all
make -C materials libc-check
make -C materials check
```

O último comando deve falhar no starter syscall. Essa falha representa trabalho pendente do participante.
`BUILD=/tmp/outro-diretorio make -C materials check` escolhe outro destino para artefatos.
Os checks usam GNU ld `--wrap` para controlar retornos; não substituem o trace real.
Consulte [o roteiro](experiments/trace.md), [os materiais](materials/README.md) e [as referências](references.md).

Licenças: código MIT; documentação CC BY 4.0; fixture CC0-1.0.

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
