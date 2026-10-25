# Laboratório de mecanismos de atenção

Implemente uma cabeça de attention para sequências pequenas, com todos os
intermediários visíveis. Comece pelo [enunciado](index.md) e pelo
[contrato](materials/contract.md).

## Preparação e execução

Execute os comandos na pasta que contém este README. Requer Python 3.10 ou
posterior e biblioteca padrão; não há instalação de pacotes.

```bash
python3 --version
python3 -c 'import sys; print(sys.float_info)'
python3 checks/verify_fixtures.py
python3 checks/test_support.py
python3 checks/check.py
```

Os dois primeiros scripts de checks devem retornar status 0. O último retorna
status 1 com `NotImplementedError` enquanto o starter estiver incompleto.
Depois de implementar, esse mesmo comando deve passar. Não remova casos nem
substitua a implementação por respostas codificadas a partir dos fixtures.

O [guia de materiais](materials/README.md) detalha os arquivos. O
[roteiro de memória](experiments/README.md) fornece os comandos de teoria e
medição. Para testar uma variante compatível, use
`python3 checks/check.py /caminho/attention.py`.

## Entrega

Entregue código, evidências dos checks, explicação numérica e CSV com dimensões
e repetições no [modelo de relato](report-template.md). Esse arquivo é gerado
do template compartilhado do repositório para manter o pacote independente.
As [referências](references.md) são aprofundamento depois da implementação.

## Licenças

Código autoral: MIT. Fixtures: CC0-1.0. Documentação: CC BY 4.0.
Os links de terceiros não transferem a licença do material referenciado.

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
