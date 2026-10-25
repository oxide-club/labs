# Guia local — Segurança de Memória

Leia [o enunciado](index.md). O starter contém um use-after-free intencional.

## Ambiente

Use Linux x86-64, Python 3 e GCC ou Clang com AddressSanitizer e LeakSanitizer.
Não há dependências Python externas. Registre `cc --version` e `uname -m`.
A disponibilidade de LeakSanitizer depende do sistema e do runtime.

## Preparar e executar

A partir deste diretório, antes de editar:

```sh
python3 materials/experiments/observe.py /tmp/oxide-memory-observation
```

Escolha um diretório de saída novo. O script compila com C11, `-O0 -g`, ASan e
frame pointers; limita a execução a dez segundos e registra stdout, stderr e
status. O status zero do script significa que observou o diagnóstico esperado;
o programa filho deve terminar com erro. Veja [o guia dos materiais](materials/README.md).
Edite `materials/starter/lifetime.c` e `materials/starter/variation.c`.

## Verificar

```sh
python3 materials/checks/check.py
```

O starter deve falhar. Após concluir o núcleo, espere `16 casos; 0 falhas` e
status zero. `CC=clang python3 materials/checks/check.py` seleciona Clang.
Falhas de compilação, timeout ou runtime não são aprovação. Não desative a
verificação de memory leaks para concluir o laboratório. Se o runtime não conseguir
iniciar no ambiente restrito, registre a limitação e repita num Linux compatível.

## Registrar

Use [o modelo de relato](report-template.md). Inclua diagnóstico inicial, patch,
saídas dos checks e explicação de por que os limites são validados antes da visão.
Não trate endereços ou PIDs do diagnóstico como valores estáveis.

## Licenças

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
