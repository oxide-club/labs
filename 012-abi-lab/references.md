# Referências orientadas

Consulta em 25/10/2026. Nenhum código externo foi incorporado.

- [System V AMD64 psABI — fontes da especificação](https://gitlab.com/x86-psABIs/x86-64-ABI): consulte passagem de parâmetros, registradores e alinhamento. A página abi.tex foi acessível, mas as regras ficam no capítulo low-level-sys-info; a revisão do projeto é móvel. Pergunta: por que a entrada observa oito bytes além do alinhamento anterior ao call?
- [libffi v3.4.6, src/x86/ffi64.c](https://github.com/libffi/libffi/blob/3d0ce1e6fcf19f853894862abcbac0ae78a7be60/src/x86/ffi64.c): arquivo real verificado via raw, incluindo MAX_GPR_REGS, register_args e classify_argument. Organiza chamadas de tipos variados; o exercício trata somente oito inteiros. Observe a separação entre classificação e preparação da área de argumentos. Pergunta: por que seis registradores gerais não bastam para descrever todas as assinaturas? O SHA 3d0ce1e6fcf19f853894862abcbac0ae78a7be60 foi obtido com git ls-remote para a tag v3.4.6.
- [musl v1.2.5, memcpy.s](https://github.com/ifduyue/musl/blob/v1.2.5/src/string/x86_64/memcpy.s): referência curricular para uma função assembly de produção. O acesso raw falhou nesta preparação; leitura pendente, sem atribuir verificação ao arquivo. Ao consultá-lo, identifique parâmetros e retorno e compare uma função folha com nossa chamada interna ao probe.
- [Zhirkov, Low-Level Programming, capítulo 14](https://link.springer.com/book/10.1007/978-1-4842-2403-8): suporte curricular para tradução e frames. Livro não consultado integralmente nesta preparação.
- [Manual oficial do GDB](https://sourceware.org/gdb/current/onlinedocs/gdb.html): consulta para breakpoints, registradores e exame de memória; use os comandos locais do experimento como roteiro.

O algoritmo define a soma; a ABI define como os módulos trocam valores e preservam estado.
Explique essa distinção com um caso cujo resultado esteja certo, mas cujo callee-saved esteja corrompido.
