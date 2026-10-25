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
