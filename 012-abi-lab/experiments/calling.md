# Observar chamadas entre módulos

Parta da raiz deste laboratório. Registre `uname -m`, `gcc --version`, `clang --version` e `objdump --version`.
Use `/tmp/oxide-abi-observe` como diretório exclusivo para artefatos descartáveis:

```sh
mkdir -p /tmp/oxide-abi-observe
gcc -std=c11 -g -O0 -fno-inline -c materials/calls.c -o /tmp/oxide-abi-observe/calls-gcc.o
objdump -dr /tmp/oxide-abi-observe/calls-gcc.o
clang -std=c11 -g -O0 -fno-inline -c materials/calls.c -o /tmp/oxide-abi-observe/calls-clang.o
objdump -dr /tmp/oxide-abi-observe/calls-clang.o
```

Preveja onde cada função obtém seus argumentos. Observe a função com oito parâmetros:
quais valores chegam por memória? Registre a origem relativa ao frame escolhido pelo compilador.
Explique por que esse offset pode mudar em O2. Repita as compilações com `-O2`.
A ausência de frame pointer não significa ausência de contrato de stack.

Para observar chamadas reais, construa uma versão persistente dos checks:

```sh
gcc -std=c11 -g -O0 -I materials checks/check.c checks/probe.S materials/calls.c materials/arithmetic.S -o /tmp/oxide-abi-observe/check
printf '1 2 3 4 5 6 7 8 204\n' > /tmp/oxide-abi-observe/input.txt
gdb /tmp/oxide-abi-observe/check
```

No GDB, execute:

```text
break arithmetic8
run < /tmp/oxide-abi-observe/input.txt
info registers rdi rsi rdx rcx r8 r9 rsp
x/3gx $rsp
print/x ((unsigned long)$rsp & 15)
break alignment_probe
continue
```

Na entrada de arithmetic8, os três words são endereço de retorno, argumento 7 e argumento 8.
Isso vale nesse instante, antes de instruções que movam rsp. O resto da stack depende do frame.
No starter, alignment_probe nunca é atingido; após implementar, o breakpoint deve ser atingido
uma vez, com rsp módulo 16 igual a oito. Observe os registradores após retornar do probe:
quais argumentos desapareceram e onde sua implementação guardou cópias?

Verifique primeiro os resultados. Depois explique diferenças entre compiladores.
Não existe sequência de instruções normativa para a soma ponderada.
