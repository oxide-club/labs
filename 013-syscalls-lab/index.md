---
title: Laboratório de Syscalls
area: operating-systems
slug: 013-syscalls-lab
summary: Compare write da libc com syscall e trate retornos parciais e erros.
question: Onde termina a interface C e começa a interface de syscalls?
draft: false
publishedAt: 2026-10-25
topics: [Syscalls, Linux, I/O]
prerequisites: [C, File descriptors, Processos]
tools: [cc, strace, objdump, Python 3]
environment: Linux x86-64 com libc e GNU toolchain
difficulty: intermediate
---

## O que vamos investigar

### O que você vai implementar e comparar

Você vai **completar uma função que escreve todos os bytes pedidos, mesmo quando
uma chamada escreve apenas parte deles**, e comparar duas formas de solicitar
a escrita ao Linux.

A variante que usa `write` da libc está pronta. Complete `write_all` em
`materials/starter/write_syscall.c`, usando `syscall(SYS_write, ...)`.

```text
pedido: escrever "oxide\n" (6 bytes)
primeira chamada confirma 2 → faltam 4 → continuar a partir do terceiro byte
```

Esse exemplo descreve um cenário possível de retorno parcial, não uma divisão
que toda execução precisa apresentar. Os checks simulam retornos parciais e
interrupções para verificar sua lógica. O `strace` mostra o que ocorreu em uma
execução real.

Entregue as duas variantes funcionais, os resultados dos checks e traces de
sucesso e de file descriptor inválido. Explique o caminho programa → libc → kernel,
incluindo o retorno e `errno`. Nesta tarefa, `syscall()` ainda é uma função da
libc; escrever o ponto de entrada do programa em assembly é opcional.

### Conceitos para a investigação

Uma syscall transfere o controle do programa para o kernel.
Uma função de biblioteca pode preparar essa transição. Você vai comparar duas
interfaces C para a mesma operação e explicar o que o trace permite observar.

#### Contrato técnico

Ambiente obrigatório: Linux x86-64, C11 e libc. Cada fonte exporta
`int write_all(int fd, const void *buf, size_t length)`; compile uma variante por vez.
O tamanho deve respeitar `length <= 1048576`. Quando `length` for positivo, `buf`
deve apontar para essa quantidade de bytes legíveis. Quando for zero, a função
aceita `NULL`, retorna 0 e não chama a operação de escrita subjacente (backend).
Sucesso retorna 0 após transmitir todos os bytes, em ordem e sem repetição.
Retorno positivo parcial avança apenas pelos bytes confirmados. `-1/EINTR` repete o trecho pendente.
Outro erro retorna -1, preserva o `errno` do backend e não repete a chamada.
Bytes já escritos permanecem escritos após falha; não existe rollback.
Retorno zero do backend com bytes pendentes termina com -1/EIO, sem laço infinito.
O valor de `errno` após sucesso não faz parte do contrato.
A variante pronta chama `write`; a variante do participante deve chamar
`syscall(SYS_write, fd, buffer, count)`, sem substituir por `write`.
`syscall()` ainda é uma função da libc; ela apresenta -1 e `errno`, não o erro bruto negativo do kernel.

CLI sem argumentos escreve exatamente `oxide\n` em stdout e retorna 0.
`--bad-fd` tenta escrever em -1, não emite stdout, informa `EBADF` em stderr e retorna 1.
Falhas diferentes informam `write failed`; argumentos inválidos retornam 2.
Os checks controlam retornos para testar escrita parcial e EINTR; não afirmam que sinais reais foram entregues.

## Antes de começar

### Linguagens e ambiente

A implementação de referência usa **C11** em Linux x86-64. Rust e assembly x86-64
são alternativas recomendadas, desde que o contrato seja adaptado explicitamente.
Em qualquer implementação, preserve a ABI de syscall e explique a distinção
entre a interface da libc e a do kernel.

Os materiais fornecem código inicial em C11. Consulte no guia abaixo as adaptações
necessárias para outras linguagens.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Conheça pointers, errno, file descriptors e valores de retorno em C.
Instale compilador C, GNU binutils, GNU coreutils (timeout), make, Python 3 e strace. Registre versões e `uname -m`.
Execute comandos na raiz deste pacote. Não são necessárias permissões administrativas.
Se ptrace estiver bloqueado, registre a restrição e realize a observação em um Linux que permita strace.

## Materiais

Leia [o guia de execução](README.md) e [o inventário](materials/README.md).
O exemplo libc está completo; o arquivo syscall compila, mas retorna ENOSYS enquanto o TODO existir.
Os checks e o roteiro de trace estão incluídos.

## Etapas da investigação

1. **Prever:** liste operações necessárias para escrever seis bytes e encerrar. Separe essa previsão da inicialização da libc.
2. **Observar:** execute `make -C materials libc-check` e o roteiro [de trace](experiments/trace.md). Guarde stdout e linhas write relevantes.
3. **Explicar:** relacione argumentos, bytes pedidos, retorno e errno. Diferencie observação real e retorno simulado.
4. **Implementar:** complete somente `materials/starter/write_syscall.c`. Preserve o contrato de retomada e erro.
5. **Verificar:** execute `make -C materials check`. Os mesmos cenários devem passar para ambas as variantes.
6. **Comparar:** gere disassembly conforme o roteiro. Desenhe programa → libc → instrução syscall → kernel → retorno.
   Para Linux x86-64, identifique rax (número/resultado) e rdi/rsi/rdx/r10/r8/r9 (argumentos).
   Explique por que o quarto argumento de função C usa rcx, enquanto a syscall usa r10; syscall destrói rcx e r11.

## Critérios de conclusão

Entregue duas variantes funcionais, checks aprovados, comandos e versões, trace de sucesso e EBADF,
e explicação da API C, ABI de syscall e conversão de erro. Não exija sequência fixa de startup, PID ou endereço.
Inclua hipótese, observações e limitações no relatório. Use [o modelo de relatório](report-template.md).

## Extensões opcionais

Investigue `_start` em assembly ou provoque EINTR com pipe e sinais reais, usando timeout e limpeza.
Explique por que uma escrita em pipe fechado pode produzir SIGPIPE antes de o programa tratar EPIPE.
Essas extensões não substituem os testes da implementação exigida.

## Participação no clube

Compartilhe uma tentativa com comando, ambiente, resultado esperado e observado.
Inclua somente trechos relevantes do trace e explique o que ainda não compreendeu.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md) depois de investigar o exemplo.
Retome os conceitos de processos, compilação e ABI ao explicar a fronteira usuário/kernel.
