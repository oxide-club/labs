# Guia local — Protocolos Binários

Leia [o enunciado](index.md). Use Python 3.10+ e biblioteca padrão.
Todos os comandos partem deste diretório:

```sh
python3 checks/check.py
python3 experiments/trace.py
```

Complete `materials/protocol.py`. O starter importa, mas os comandos terminam com status 1 e `NotImplementedError`.
Essa rejeição é esperada até implementar o mecanismo. Os checks não exigem rede, sockets ou pacotes externos.
Consulte [os materiais](materials/README.md) e [o experimento](experiments/fragmentation.md).
Registre sua investigação no [modelo de relato](report-template.md), gerado do modelo central.

Documentação original: CC BY 4.0. Código original: MIT. Fixtures originais: CC0 1.0.
Fontes externas mantêm suas próprias licenças.

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

`make run` observa o parser de referência com os vetores do roteiro; o starter
Python incompleto pode falhar. Para usar a variante Go:

```sh
make setup VARIANT=go
make build VARIANT=go
make test VARIANT=go
make run VARIANT=go
```

Na variante Go, `run` valida os vetores independentes do parser; seu sucesso
não aprova a solução. `test` verifica o parser e rejeita o starter incompleto.
