# Laboratório de Memory Allocation

Implemente uma arena C11 sobre `malloc`, com alinhamento, falhas sem consumo de
estado e descarte coletivo. Leia [o enunciado](index.md) e execute os comandos do
[guia de materiais](materials/README.md). O starter compila, mas está incompleto:
o check principal deve retornar status 1 antes da implementação.

Entregue código, checks adicionais e relato. O pacote inclui `report-template.md`,
gerado a partir do [modelo compartilhado](report-template.md).
O pool com liberação individual é opcional e deve ficar separado.

Licenças: código MIT; fixtures CC0-1.0; documentação CC BY 4.0.

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

`make run` demonstra alinhamento e layout de memória. `make test` verifica a
arena, incluindo falha de alocação; o starter incompleto continua sendo rejeitado.
