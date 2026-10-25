# Trace e disassembly

Preveja a escrita, depois execute:

```sh
make -C materials all
strace -o /tmp/oxide-libc.trace -e trace=write materials/build/write_libc > /tmp/oxide-libc.out
cmp materials/expected.txt /tmp/oxide-libc.out
strace -o /tmp/oxide-bad.trace -e trace=write materials/build/write_libc --bad-fd
objdump -d materials/build/write_libc > /tmp/oxide-libc.asm
objdump -d materials/build/write_syscall > /tmp/oxide-syscall.asm
```

A execução com `--bad-fd` deve terminar com status 1. Localize `write(-1, ...) = -1 EBADF`;
a linha write para stderr pertence ao diagnóstico do programa.
No sucesso, localize `write(1, "oxide\n", 6) = 6`. Não compare todo o arquivo de trace literalmente.
Após implementar, repita os comandos com `write_syscall` e novos nomes de saída.
Use `strace -o /tmp/oxide-full.trace ...` sem filtro para observar inicialização, sem exigir lista ou contagem fixa.

Identifique as chamadas de função write/syscall no disassembly. Uma chamada PLT não mostra por si só
os registradores na instrução de entrada no kernel. Use a especificação para separar as duas convenções.
O trace mostra operações do kernel, mas não identifica sozinho qual wrapper C as originou.
Nos checks simulados, registre os bytes aceitos antes do erro e explique por que não devem ser reenviados.
