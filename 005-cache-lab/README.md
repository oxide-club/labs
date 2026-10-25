# Cache e Localidade — guia local

Leia [o enunciado](index.md). Ele define o modelo e a investigação obrigatória.
Use C11 com `uint64_t`, GCC ou Clang e Python 3 em um terminal Linux.

## Compilar

A partir deste diretório:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/starter/cache.c -o cache
```

O starter compila, mas retorna uma mensagem de tarefa incompleta.
Implemente o simulador antes de executar as verificações de solução.

## Executar e verificar

```sh
./cache < materials/inputs/trace-a.txt
./cache < materials/inputs/trace-b.txt
python3 checks/check.py ./cache
```

O check retorna zero se os seis casos públicos passarem; retorna 1 se algum falhar.
Os traces A e B devem produzir respectivamente `3/5/3` e `4/12/8` para hits/misses/evictions.
Registre a previsão antes de consultar esses resultados.

Crie também o gerador de percursos exigido no enunciado.
Execute cada trace de matriz em um novo processo do simulador.
As contagens representam o modelo; não são medições de uma CPU.

Use [o modelo de relato](report-template.md) e consulte [as referências orientadas](references.md) após o núcleo.
Documentação original: CC BY 4.0. Código original: MIT. Traces originais: CC0 1.0.

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

`make run` alimenta o simulador com `materials/inputs/trace-a.txt`. O starter
incompleto pode falhar tanto nesse experimento quanto nos checks.

A variante Rust usa os mesmos contratos públicos e exige `rustc`:

```sh
make setup VARIANT=rust
make build VARIANT=rust
make test VARIANT=rust
make run VARIANT=rust
```

Sem o seletor, a implementação de referência em C é usada.
