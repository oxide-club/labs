# Compilação e Execução

Leia o [enunciado](index.md) e o [guia dos materiais](materials/README.md).
O código auxiliar está completo; a entrega é uma investigação com evidências anotadas.

```sh
cd materials
make
make check
make observe
```

Os checks devem retornar 0. Os dois erros de linking são esperados e verificados pelos checks.
`make observe` informa quando falta `strace`; não trate coleta parcial como conclusão integral.
Use o [modelo central de relato](report-template.md). No pacote, use o modelo incluído na raiz.

Documentação original: CC BY 4.0. Código original: MIT. Dados originais: CC0 1.0.
Os fontes externos são apenas referências; não foram copiados para o pacote.

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
