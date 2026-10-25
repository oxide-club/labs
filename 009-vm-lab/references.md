# Referências orientadas — Máquinas Virtuais

Verificação dos arquivos Lua e CPython em 25/10/2026. As fontes são leituras externas; nenhum código de terceiros foi copiado.

- [Crafting Interpreters — A Bytecode Virtual Machine](https://craftinginterpreters.com/a-bytecode-virtual-machine.html): leia a introdução da Parte III e observe a separação entre representação e execução. O formato deste laboratório é textual e tem contrato próprio.
- [Lua 5.4.7 — lvm.c](https://github.com/lua/lua/blob/v5.4.7/lvm.c): arquivo consultado; localizados `luaV_execute` e operações aritméticas. Procure busca de instrução, alteração do PC e dispatch. Lua usa registradores; compare seus operandos com a stack desta VM.
- [CPython 3.13.0 — Python/ceval.c](https://github.com/python/cpython/blob/v3.13.0/Python/ceval.c): localizados `_PyEval_EvalFrameDefault`, `DISPATCH` e inclusão de `generated_cases.c.h`. O ciclo usa frames, ponteiro de instruções e stack; os casos de instruções não ficam todos neste arquivo.
- [Zhirkov — Low-Level Programming](https://link.springer.com/book/10.1007/978-1-4842-2403-8): o capítulo 7 contextualiza modelos de computação. Leitura complementar; não é necessário acesso ao livro para concluir o núcleo.

O acesso direto ao capítulo de Crafting Interpreters falhou nesta preparação (HTTP 400); a referência curricular foi preservada, sem afirmar leitura remota nesta sessão. O livro de Zhirkov não foi usado como oráculo.

Os links de código estão fixados em tags de versão. A API de resolução de tags para SHA ficou indisponível no acesso de preparação; não foi inventado um SHA.
Pergunta de leitura: quais invariantes adicionais surgem quando a VM passa a executar chamadas, objetos e exceções?
