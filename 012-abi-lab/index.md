---
title: Laboratório de ABI e Calling Conventions
slug: 012-abi-lab
summary: Investigue argumentos, preservação de registradores e alinhamento entre C e assembly.
question: Como módulos compilados separadamente concordam sobre uma chamada?
draft: false
publishedAt: 2026-10-25
topics: [ABI, Assembly, Calling conventions]
prerequisites: [C, Ponteiros, Stack, Object files]
tools: [GCC, Clang, GNU assembler, objdump, GDB, Python 3]
environment: Linux x86-64 com System V AMD64 LP64 e GNU assembly
difficulty: advanced
---

## O que vamos investigar

Uma ABI define o contrato binário entre módulos: onde ficam argumentos e resultados,
quais registradores sobrevivem a uma chamada e como alinhar a stack.
Observe funções C com 1, 3, 6 e 8 argumentos e implemente uma função assembly que chama outra função.

### Contrato técnico

Use Linux x86-64, modelo LP64, System V AMD64, C11 e GNU assembly em sintaxe AT&T.
Todos os argumentos e resultados são `uint64_t`. A aritmética ocorre módulo 2^64;
qualquer padrão de 64 bits é válido, sem overflow com sinal ou entrada a rejeitar.
As assinaturas completas estão em [arithmetic.h](materials/arithmetic.h).
`call1`, `call3`, `call6` e `call8` retornam a soma ponderada `a1 + 2*a2 + ... + n*an`.
São referências completas em C para observação, sem efeitos externos.

Implemente `arithmetic8` em [arithmetic.S](materials/arithmetic.S), como object file separado,
com os mesmos oito argumentos e resultado de `call8`. Chame `alignment_probe(void)` exatamente
uma vez por invocação, antes de retornar. Não substitua o cálculo por chamada à referência C.
O probe não retorna dados úteis, pode destruir todos os registradores caller-saved e registra
seu alinhamento de entrada. Preserve os argumentos necessários para o cálculo através dessa chamada.
Não leia nem escreva os globais `probe_count` e `probe_alignment` na implementação.
Eles pertencem exclusivamente à instrumentação dos checks. Fora do probe, não há efeitos externos.

Para estes argumentos inteiros, os seis primeiros chegam em `rdi, rsi, rdx, rcx, r8, r9`;
os demais chegam na stack. O resultado retorna em `rax`.
Preserve `rbx, rbp, r12, r13, r14, r15` e restaure `rsp` antes de retornar.
Mantenha o direction flag limpo; não modifique o ambiente de ponto flutuante.
Imediatamente antes de `call`, `rsp` deve ser múltiplo de 16; na entrada do chamado,
`rsp % 16 == 8`, porque o endereço de retorno ocupa oito bytes.
Offsets relativos à entrada deixam de valer quando a função move `rsp`: derive-os do seu frame.
Não use a red zone para dados que precisam sobreviver a uma chamada.
Não há requisitos sobre prólogo, escolha de instruções ou uso de frame pointer.
Structs, vetores SIMD, varargs, Windows x64 e outras arquiteturas ficam fora do núcleo.

## Antes de começar

### Linguagens e ambiente

Referência: **C + GNU assembly**. Aceitas: C e assembly no núcleo; Rust como extensão FFI.
Recomendadas: Rust para extensão FFI. Linux x86-64, System V AMD64 LP64, alinhamento e registradores preservados.
Materiais oficiais: C + GNU assembly existente.
Equivalência: apenas comparativa para a extensão FFI.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
A restrição preserva o mecanismo observado no núcleo.

Conheça funções e ponteiros em C, stack e leitura básica de assembly.
Instale compilador C, GNU binutils, Python 3 e GDB. Leia [o guia local](README.md).
Os checks exigem Linux x86-64 e encerram explicitamente em ambiente incompatível.

## Materiais

[O guia dos materiais](materials/README.md) descreve fontes e [vetores independentes](materials/vectors.json).
[Os checks](checks/check.py) compilam o starter e testam resultado e invariantes.
[O experimento](experiments/calling.md) orienta a observação com GCC, Clang e GDB.

## Etapas da investigação

1. **Prever:** desenhe a localização dos oito argumentos antes de abrir o disassembly. Calcule os resultados dos vetores ordered e stack8.
2. **Observar:** compile calls.c com O0 e inspecione as quatro funções. Registre trechos e uma captura dos argumentos na entrada de arithmetic8.
3. **Explicar:** desenhe registradores e stack antes de call, na entrada e após ret. Separe endereço de retorno, argumentos e armazenamento local.
4. **Implementar:** complete arithmetic8 e explique como preservou argumentos durante alignment_probe. Não altere o probe para obter aprovação.
5. **Verificar:** execute os checks em O0 e O2; compare GCC e Clang com os comandos do experimento. Explique diferenças sem exigir instruções idênticas.

## Critérios de conclusão

Os checks devem terminar com status zero para os dois níveis de otimização.
Entregue fonte assembly, comandos, tabela de registradores e diagrama de stack.
Explique o alinhamento na chamada interna e a preservação de callee-saved.
Registre resultados dos dois compiladores ou a indisponibilidade de um deles.
Os checks cobrem resultados, sentinels e alinhamento observado; revisão do código continua
necessária para direction flag, acessos válidos à stack e todos os caminhos da função.

## Extensões opcionais

Investigue retorno de uma struct de dois inteiros ou uma interface Rust/C.
Consulte a classificação da ABI antes de prever o comportamento. Mantenha a interface obrigatória.

## Participação no clube

Compartilhe previsão, comando e menor vetor que divergiu. Use [o modelo de relato](report-template.md).
Inclua versões do compilador e flags, sem tratar um único disassembly como regra universal.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md) após observar seu próprio código.
Relacione o resultado à compilação separada, ao linking e à FFI.
