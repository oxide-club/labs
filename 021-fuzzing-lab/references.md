# Referências orientadas — Fuzzing e análise de falhas

- [LLVM — libFuzzer](https://llvm.org/docs/LibFuzzer.html): ler contrato do target, corpus, opções de limite e minimização.
- [Rust Fuzz Book — tutorial de cargo-fuzz](https://rust-fuzz.github.io/book/cargo-fuzz/tutorial.html): seguir o percurso entre target, artifact, reprodução e minimização.
- [Clang — ASan](https://clang.llvm.org/docs/AddressSanitizer.html) e [UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html): identificar quais sintomas a configuração selecionada pode detectar.
- **Código real:** [LLVM — FuzzerDriver.cpp](https://github.com/llvm/llvm-project/blob/llvmorg-20.1.8/compiler-rt/lib/fuzzer/FuzzerDriver.cpp). Ler `RunOneTest` e `MinimizeCrashInput`; distinguir reprodução, redução do caso e campanha de descoberta. A infraestrutura do motor não é o parser didático.

## Situação das referências

Consulta em 25/10/2026: documentação oficial de libFuzzer, ASan e UBSan e código `FuzzerDriver.cpp` na tag `llvmorg-20.1.8`. A página GitHub não respondeu nesta consulta; o [fonte bruto da mesma tag](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-20.1.8/compiler-rt/lib/fuzzer/FuzzerDriver.cpp) foi lido. Essa revisão orienta a leitura; a toolchain local validada foi Clang 23.1.3.

`RunOneTest` executa um arquivo fixo; `MinimizeCrashInput` repete execuções e compara tokens de diagnóstico. Pergunta: por que reproduzir uma entrada não equivale a executar uma campanha, e por que apenas reduzir o comprimento não identifica a causa? O arquivo também mostra fiscalização periódica do RSS. Esses mecanismos pertencem ao motor, enquanto o exercício investiga OXF1. Nenhum trecho desse código foi incorporado aos materiais.

A leitura Rust permanece como alternativa; cargo-fuzz não foi validado nesta preparação.

A implementação real pode ter requisitos de portabilidade, desempenho e compatibilidade além do experimento. Use a pergunta de leitura para explicar essa diferença; não copie o código como solução didática. As leituras exigidas no roteiro continuam parte da investigação.
