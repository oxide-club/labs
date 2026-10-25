---
title: Laboratório de Shared Libraries e Dynamic Linking
area: compilation-execution
slug: 014-dynamic-linking-lab
summary: Compare archives e shared objects e implemente carregamento explícito com diagnóstico de erros.
question: Como o executável utiliza código de uma biblioteca em outro arquivo?
draft: false
publishedAt: 2026-10-25
topics: [Linking, ELF, Shared libraries]
prerequisites: [C, Compilação separada, Símbolos]
tools: [GCC, binutils, Python 3]
environment: Linux x86-64 com dynamic loader ELF
difficulty: intermediate
---

## O que vamos investigar

### O que você vai comparar e construir

Você vai **comparar três formas de usar funções de uma biblioteca**. A biblioteca
com soma e quadrado e dois clientes já estão prontos. Sua implementação será
o terceiro cliente, `dynamic.c`.

| Cliente | Como obtém o código da biblioteca |
| --- | --- |
| `archive-client` | Incorpora código de `liboxide.a` durante o linking. |
| `shared-client` | Depende de `liboxide.so`, carregada para executar o programa. |
| `dynamic` | Abre explicitamente a biblioteca com `dlopen` e busca uma função com `dlsym`. |

No modo `call`, ao escolher `oxide_add`, seu cliente deve chamar a função com
os argumentos 3 e 4 e imprimir `7` seguido de newline após fechar a biblioteca
com sucesso. No modo `skip`, apenas abre e fecha a biblioteca.

O trabalho inclui tratar biblioteca ausente, símbolo ausente e fechamento do
handle, além de observar a resolução imediata (`now`) ou adiada (`lazy`).
Entregue o cliente, checks e um relato com dependências, símbolos, tamanhos dos
arquivos e experiências de falha. O contrato abaixo fixa a CLI e os códigos de erro.

### Conceitos para a investigação

Uma shared library mantém código em um arquivo carregado durante a execução.
Você vai comparar esse mecanismo com a incorporação de código de uma static library (archive) durante o linking. A investigação mostra em que
momento as referências a funções precisam ser resolvidas.

#### Contrato técnico

O [contrato completo](materials/contract.md) fixa API, CLI, estados após falhas e limites.
A biblioteca fornece funções de soma e quadrado. Dois clientes completos permitem
comparar static linking com dynamic linking. Sua tarefa é implementar `dynamic.c`,
que carrega a biblioteca explicitamente com `dlopen` e `dlsym`.
O archive não torna o executável inteiro estático. O contrato não exige `-static` nem libc estática.

## Antes de começar

### Linguagens e ambiente

A parte obrigatória usa **C11 em Linux x86-64/ELF**. A investigação envolve `dlopen`, `dlsym`,
position-independent code (PIC), símbolos e lifetime do handle da
biblioteca. Os materiais fornecem código em C11.

Rust e C++ são recomendados para extensões de interoperabilidade. Essas comparações
complementam a investigação obrigatória em C/ELF, mas não a substituem.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

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
   (position-independent code) e por que uma relocation não é simplesmente uma chamada de função.
4. **Implementar:** complete o carregamento explícito conforme o contrato; trate erros e lifetime do handle.
5. **Verificar:** execute `python3 checks/check.py`. O starter compila, mas deve falhar nos checks de `dynamic`.
   Faça as experiências de falha e de resolução no roteiro. Registre comandos, status e stderr.

## Critérios de conclusão

Os checks passam após a implementação. O relatório identifica exports, dependências e relocations;
compara os clientes sem deduzir regras universais de tamanho; demonstra biblioteca ausente e
símbolo renomeado; explica diferenças entre NOW e LAZY e limitações do ambiente.
Apresente a limpeza dos handles também nos caminhos de erro; os checks não provam esse invariante.

## Extensões opcionais

Investigue SONAME, versionamento de ABI, visibilidade, GOT e PLT após concluir as etapas obrigatórias.
Compare o efeito de `-Wl,-z,now`; registre flags e toolchain.

## Participação no clube

Compartilhe hipótese, comandos, trechos de ELF e uma pergunta específica. Diferencie falha esperada
da fixture de falha da implementação. Inclua libc, linker e flags para permitir reprodução.

## Referências e atividades relacionadas

Consulte as [leituras orientadas](references.md). Compilação e ABI ajudam a interpretar símbolos;
este pacote inclui todos os materiais locais necessários às etapas obrigatórias.
