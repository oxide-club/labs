# Referências orientadas — Segurança de Memória

## Leitura principal

[Clang — AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html),
seções *Usage*, *Symbolizing the Reports* e *Memory leak detection*. Leia como
compilar, interpretar as três origens do diagnóstico e ativar a detecção de
memory leaks. Documento oficial consultado em 2026-10-25. A disponibilidade de
LeakSanitizer varia entre plataformas. Ausência de diagnóstico não é prova geral.

O livro de Igor Zhirkov, [Low-Level Programming](https://link.springer.com/book/10.1007/978-1-4842-2403-8),
caps. 11 a 13, é uma leitura complementar indicada pelo currículo. O conteúdo
comercial dos capítulos não foi consultado nesta preparação e não é necessário
para executar os comandos do laboratório.

## Contrato da linguagem

[C11, rascunho público N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf):
consulte 6.2.4 para lifetime, 6.5.6 para aritmética de ponteiros e 7.22.3 para
allocation dinâmica. O arquivo é uma indicação normativa para consulta; a leitura
integral não foi feita durante a preparação. O contrato local exige validar 11
antes de formar a visão, mesmo que o ponteiro one-past possa ser formado sem
leitura no modelo de arrays. Uma visão usada como string precisa de terminador
acessível durante o lifetime do bloco.

## Código real — após concluir o núcleo

Os dois arquivos abaixo foram lidos na revisão LLVM `87f0227cb60147a26a1eeb4fb06e3b505e9c7261`
(tag `llvmorg-20.1.8`), em 2026-10-25. São referências externas em C++ e conservam
as licenças do projeto LLVM. Não foram incorporados ao starter.

### Teste real de use-after-free

[LLVM/compiler-rt — use-after-free.cpp, revisão fixada](https://github.com/llvm/llvm-project/blob/87f0227cb60147a26a1eeb4fb06e3b505e9c7261/compiler-rt/test/asan/TestCases/use-after-free.cpp)
é um teste de regressão real. Em `main`, `malloc` cria dez bytes, `free` libera o
bloco e `x[5]` provoca uma leitura inválida. As diretivas `RUN` exercitam níveis
`-O0` a `-O3`. Os padrões `CHECK` correlacionam acesso, liberação e allocation,
permitindo endereços variáveis. Observe como `FileCheck` reconhece o mecanismo
sem fixar os endereços. Diferentemente do laboratório, o teste deve continuar
falhando; não é um exercício para corrigir sua ordem de operações.

Pergunta: por que um teste de regressão do detector precisa esperar uma falha do
programa, enquanto nossos checks da correção precisam esperar sucesso?

### Alocador instrumentado de produção

[LLVM/compiler-rt — asan_allocator.cpp, revisão fixada](https://github.com/llvm/llvm-project/blob/87f0227cb60147a26a1eeb4fb06e3b505e9c7261/compiler-rt/lib/asan/asan_allocator.cpp)
implementa parte do alocador do runtime ASan. Observe `CHUNK_QUARANTINE`,
`QuarantineCallback` e suas chamadas a `PoisonShadow`. Elas associam estado e
informação de memória auxiliar aos blocos liberados. O runtime administra
quarentena e reciclagem; o programa do laboratório apenas usa `malloc` e `free`.
Esta leitura é avançada e não bloqueia a conclusão do núcleo.

Pergunta: como a quarentena ajuda a observar acessos depois de `free`, e por que
ela não prolonga o lifetime do objeto no modelo de C?

## Aprofundamento opcional

[Clang — LeakSanitizer](https://clang.llvm.org/docs/LeakSanitizer.html) explica a
verificação complementar de memory leaks. Compare depois com lifetime e borrowing
em Rust. Essas leituras não substituem a justificativa da ordem dos acessos em C.
