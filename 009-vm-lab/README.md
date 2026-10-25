# Guia local — Máquinas Virtuais

Leia [o enunciado](index.md). Use Python 3.10+ e biblioteca padrão; não é necessário instalar pacotes.

Execute a partir deste diretório:

```sh
python3 checks/check.py
```

Edite `materials/vm.py`. O starter é sintaticamente válido, mas o check termina com status 1 e `NotImplementedError`.
Essa rejeição é esperada. Após implementar o contrato, o mesmo comando deve retornar 0.
Os checks carregam o módulo local, sem executar código textual como Python.

Siga [o experimento](experiments/trace.md) e registre os resultados no [modelo de relato](report-template.md).
O modelo é gerado a partir do modelo central, sem manutenção manual de cópias.
Documentação original: CC BY 4.0. Código original: MIT. Fixtures originais: CC0 1.0.
As referências externas mantêm suas próprias licenças.

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
