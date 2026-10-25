# Laboratório de Processos e Pipes

Implemente `oxrun` sem parser de shell. O [enunciado](index.md) fixa o contrato.

```sh
cd materials
make
make check
```

O starter compila, mas os checks de execução falham até a implementação do participante. Comece pelo [guia autocontido](materials/README.md). Código original: MIT; fixtures: CC0-1.0; documentação: CC BY 4.0. As referências externas conservam suas licenças; nenhum código BusyBox foi copiado.

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

`make run` solicita ao launcher o pipeline `printf "abc\n" | wc -c`.
O launcher incompleto é rejeitado; `make test` executa os checks públicos de
processos. Ambos mantêm as falhas do starter.
