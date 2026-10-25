# Laboratório de Representação Binária

Como transformar campos lógicos em uma palavra e em quatro bytes portáveis?
Comece pelo [enunciado](index.md) e siga o [guia dos materiais](materials/README.md).
O pacote contém um starter incompleto, checks públicos e vetores conhecidos; compilar
não significa concluir a atividade. Implemente as quatro funções antes de esperar
que os checks terminem com status zero.

Os comandos usam C11, GCC ou Clang e bytes de oito bits. Não há dependências externas
para executar o núcleo. As [referências](references.md) servem para consulta posterior.
Use o [modelo de relato](report-template.md) para registrar previsões e evidências.

Código original deste laboratório: MIT. Fixtures: CC0-1.0. Documentação: CC BY 4.0.
As referências externas conservam suas próprias licenças e não são redistribuídas.

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

`make run` observa a representação do pacote com o starter atual. `make test`
rejeita o codec incompleto; a observação não substitui esses checks.
