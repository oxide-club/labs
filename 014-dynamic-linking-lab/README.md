# Bibliotecas Compartilhadas e Linking Dinâmico

Leia o [enunciado](index.md) e o [contrato](materials/contract.md).

```sh
make -C materials
python3 checks/check.py
```

O build deve funcionar. Os checks do carregador falham enquanto `dynamic.c` estiver incompleto.
Registre a investigação no [modelo de relatório](report-template.md).
Documentação: CC BY 4.0; todo código original: MIT, incluindo os alvos em experiments.

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

`make run` solicita a carga de `liboxide.so`, resolve `oxide_add` com o modo
`now` e solicita a chamada. O loader incompleto falha; `make test` verifica
os contratos públicos de linking.
