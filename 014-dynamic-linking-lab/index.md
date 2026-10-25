---
title: Laboratório de Bibliotecas Compartilhadas e Linking Dinâmico
area: compilation-execution
slug: 014-dynamic-linking-lab
summary: Compare archives e shared objects e implemente carregamento explícito com diagnóstico de erros.
question: Como o executável utiliza código de uma biblioteca em outro arquivo?
draft: false
publishedAt: 2026-10-25
topics: [Linking, ELF, Bibliotecas compartilhadas]
prerequisites: [C, Compilação separada, Símbolos]
tools: [GCC, binutils, Python 3]
environment: Linux x86-64 com dynamic loader ELF
difficulty: intermediate
---

## O que vamos investigar

Uma biblioteca compartilhada mantém código em um arquivo carregado durante a execução.
Vamos comparar esse mecanismo com a incorporação de um archive no linking e investigar
quando referências a funções precisam ser resolvidas.

### Contrato técnico

O [contrato completo](materials/contract.md) fixa API, CLI, estados após falhas e limites.
A biblioteca fornece soma e quadrado. Os clientes completos comparam static linking da biblioteca
com dynamic linking; o participante implementa `dynamic.c`, que usa `dlopen` e `dlsym`.
O archive não torna o executável inteiro estático. O contrato não exige `-static` nem libc estática.

## Antes de começar

### Linguagens e ambiente

Referência: **C11**. Aceitas: C no núcleo C/ELF; Rust e C++ como extensão de interoperabilidade.
Recomendadas: Rust e C++. Linux x86-64/ELF, dlopen/dlsym, PIC, símbolos e lifetime do handle.
Materiais oficiais: C11 existente.
Equivalência: apenas comparativa para extensões.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
A restrição preserva o mecanismo observado no núcleo.

Use Linux x86-64 com compilador C11, `make`, `ar`, `readelf`, `nm` e Python 3.
Conheça headers, object files e símbolos. Execute apenas as bibliotecas locais fornecidas.
Não altere configuração do loader nem instale arquivos em diretórios do sistema.

## Materiais

Leia o [guia de materiais](materials/README.md). A biblioteca e os dois clientes são exemplos completos;
`dynamic.c` contém o TODO central. Os [checks](checks/check.py) verificam resultados e falhas controladas.
As [experiências](experiments/README.md) fornecem bibliotecas com símbolo renomeado e referência ausente.
Use o [modelo de relatório](report-template.md) e consulte as [referências](references.md).

## Etapas da investigação

1. **Prever:** desenhe quais arquivos cada cliente precisa em runtime. Preveja o resultado ao retirar apenas o `.so`.
2. **Observar:** execute `make -C materials`, depois os dois clientes em `materials/build/`.
   Meça `wc -c materials/build/archive-client materials/build/shared-client materials/build/liboxide.so`.
   Registre flags e toolchain: cada valor é o tamanho do arquivo, não o uso de memória.
   Compare também a soma cliente compartilhado + biblioteca; ela inclui o `.so` separado,
   enquanto o archive fornece código incorporado ao cliente. Nenhum total inclui a libc externa.
   Não suponha uma ordem de tamanhos nem deduza desempenho desses números.
   Use `ar t materials/build/liboxide.a`, `nm materials/build/archive-client`,
   `nm -D materials/build/liboxide.so`, `readelf -d materials/build/shared-client` e
   `readelf -r materials/build/shared-client`. Registre símbolos, NEEDED, RUNPATH e relocations.
3. **Explicar:** relacione símbolos definidos e indefinidos às dependências; explique PIC
   (código independente de posição) e por que uma relocation não é simplesmente uma chamada de função.
4. **Implementar:** complete o carregamento explícito conforme o contrato; trate erros e lifetime do handle.
5. **Verificar:** execute `python3 checks/check.py`. O starter compila, mas deve falhar nos checks de `dynamic`.
   Faça as experiências de falha e de resolução no roteiro. Registre comandos, status e stderr.

## Critérios de conclusão

Os checks passam após a implementação. O relatório identifica exports, dependências e relocations;
compara os clientes sem deduzir regras universais de tamanho; demonstra biblioteca ausente e
símbolo renomeado; explica diferenças entre NOW e LAZY e limitações do ambiente.
Apresente a limpeza dos handles também nos caminhos de erro; os checks não provam esse invariante.

## Extensões opcionais

Investigue SONAME, versionamento de ABI, visibilidade, GOT e PLT após concluir o núcleo.
Compare o efeito de `-Wl,-z,now`; registre flags e toolchain.

## Participação no clube

Compartilhe hipótese, comandos, trechos de ELF e uma pergunta específica. Diferencie falha esperada
da fixture de falha da implementação. Inclua libc, linker e flags para permitir reprodução.

## Referências e atividades relacionadas

Consulte as [leituras orientadas](references.md). Compilação e ABI ajudam a interpretar símbolos;
este pacote inclui todos os materiais locais necessários ao núcleo.
