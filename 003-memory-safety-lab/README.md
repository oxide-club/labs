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
