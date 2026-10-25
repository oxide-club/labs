# Laboratório de Segurança de Memória

Compare view, cópia e invalidação lógica. Leia o [enunciado](index.md) e registre
as hipóteses antes de executar os instrumentos completos.

```sh
python3 materials/experiments/compare.py /tmp/oxide-memory-comparison
```

Use um diretório novo. O runner preserva logs e metadados, com processos separados
e timeout. A coleta exige C11, Python 3 e ASan/LSan. Uma falha do sanitizador torna
a observação pendente; não a trate como ausência de defeito.

Siga o [guia dos materiais](materials/README.md) para as intervenções obrigatórias.
A correção antiga e a CLI de offsets continuam como [extensão opcional](materials/legacy.md).
Seus checks não são os critérios de conclusão da investigação atual.

Documentação original: CC BY 4.0. Código original: MIT. Dados originais: CC0 1.0.
Consulte [os avisos do repositório](https://github.com/oxide-club/labs/blob/main/LICENSING.md). As fontes externas mantêm
suas licenças; não foram copiadas para o starter.

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

`run` observa o use-after-free original; depois da correção, essa observação
deve deixar de passar. `test` verifica a implementação corrigida com ASan/LSan.
