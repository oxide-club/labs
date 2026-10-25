# Laboratório de Engenharia Reversa

Reconstrua a decisão de um executável usando comparações e fluxo de controle.
Leia o [enunciado](index.md), siga o [guia dos materiais](materials/README.md) e
registre a investigação no [modelo de relato](report-template.md).

O alvo está completo. O fonte original foi renomeado de `porta.c` para `gate.c`,
sem alterar mensagens ou comparações. Reserve sua leitura para o confronto final.
Ele acompanha o pacote para permitir o build; não há promessa de sigilo.

Início rápido, a partir deste diretório:

```sh
python3 materials/experiments/prepare.py /tmp/oxide-reverse-lab
python3 materials/checks/check.py /tmp/oxide-reverse-lab/gate-O0
```

Os seis checks públicos devem passar. O status 0 depende da entrada que você
deduzir e verificar depois. Consulte as [referências orientadas](references.md).

Código original: MIT. Documentação: CC BY 4.0. Dados de teste originais: CC0 1.0.

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

`test`, `run` e `verify-preparation` usam VM descartável. Prepare-a com
`make env-setup`; abra o console com `make env-shell`. A execução exige confirmação
explícita dentro da VM. `setup` e `build` não executam os binários no host.
Consulte [o ambiente reproduzível](materials/environment.md).
