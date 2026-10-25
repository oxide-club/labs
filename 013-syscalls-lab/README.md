# Syscalls

Leia [o contrato](index.md) antes de modificar o código.

```sh
make -C materials all
make -C materials libc-check
make -C materials check
```

O último comando deve falhar no starter syscall. Essa falha representa trabalho pendente do participante.
`BUILD=/tmp/outro-diretorio make -C materials check` escolhe outro destino para artefatos.
Os checks usam GNU ld `--wrap` para controlar retornos; não substituem o trace real.
Consulte [o roteiro](experiments/trace.md), [os materiais](materials/README.md) e [as referências](references.md).

Licenças: código MIT; documentação CC BY 4.0; fixture CC0-1.0.
