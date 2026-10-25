---
title: Laboratório de Compilação e Execução
area: compilation-execution
slug: 007-compilation-lab
summary: Observe a transformação de dois módulos C em um processo Linux.
question: O que acontece entre o arquivo-fonte e o processo em execução?
draft: false
publishedAt: 2026-10-25
topics: [Compilação, ELF, Processos]
prerequisites: [C, Funções, Endereços em hexadecimal]
tools: [cc, Make, Python 3, nm, readelf, objdump, strace]
environment: Linux x86-64; GCC ou Clang e GNU binutils; C11
difficulty: intermediate
---

## O que vamos investigar

O comando `cc` coordena várias ferramentas para transformar código-fonte em um
executável. Você vai investigar o pré-processamento, a tradução para assembly,
a montagem, linking e a execução.

Um object file contém código, dados, símbolos e registros de
referências que ainda precisam de ajuste, chamados relocations. O formato ELF
descreve seções para inspeção e linking, e segmentos para carregamento. Seções e
segmentos têm funções diferentes.

### Contrato técnico

Use os dois módulos completos `main.c` e `operations.c`. Preserve a global `global_value = 7`, o literal `"oxide"`, a função externa `add_global` e a chamada `printf` da libc.

Sem argumentos, `program` deve escrever exatamente `oxide result=12\n` e retornar 0.

Com `--wait`, deve escrever essa linha, descarregar stdout e aguardar um byte ou EOF em stdin; depois retorna 0.

Outro uso deve retornar 2 e escrever diagnóstico em stderr. Se uma função de I/O retornar erro, o programa deve retornar 1. Sinais externos mantêm sua semântica POSIX; não se exige converter SIGPIPE em status 1.

Produza, em comandos separados, o arquivo pré-processado `.i`, assembly `.s`, object files `.o` e executável. Inclua o fonte como primeira das cinco classes de artefatos.

Use C11, `-O0`, símbolos de depuração, sem LTO, e compile cada módulo separadamente. Não fixe instruções, endereços, nomes da libc ou caminho do interpretador como resultados universais.

Inspecione símbolos com `nm`, seções/segmentos/símbolos/relocations com `readelf` e instruções/relocations com `objdump`. Registre `add_global` nos dois object files e após linking.

Capture `/proc/PID/maps` enquanto o programa próprio aguarda entrada. Capture também uma execução com `strace`. Se a ferramenta ou a política impedir a coleta, registre a limitação; essa evidência continua pendente para a conclusão integral.

Provoque dois erros de linking: omita `operations.o`; depois forneça `operations.o` duas vezes. Ambos devem retornar status diferente de zero e citar o símbolo afetado. Preserve os objetos válidos e registre os diagnósticos; o texto exato depende do linker.

Os scripts devem limitar a espera, encerrar e executar reaping de seus próprios processos em falhas. Nenhum PID ou endereço fixo faz parte do contrato.

## Antes de começar

### Linguagens e ambiente

A parte obrigatória usa **C11 em Linux/ELF**, com etapas de compilação observáveis. Os materiais
fornecem os módulos em C11.

Rust e C++ são recomendados para comparações. Essas extensões não substituem a
investigação das etapas de compilação do programa C.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Use Linux com `/proc`, GCC ou Clang, GNU Make, binutils, Python 3 e `strace`. Saiba compilar C e ler hexadecimal; não é necessário escrever assembly. Leia o [guia dos materiais](materials/README.md). Não é necessário alterar ASLR ou a configuração da máquina.

## Materiais

O [README](README.md) oferece os comandos iniciais. Os [materiais](materials/README.md) incluem dois módulos completos, Makefile, checks e [experimento orientado](materials/experiments/investigation.md). A tarefa central é produzir e explicar evidências; o código auxiliar não contém lacunas artificiais. Use o [modelo central de relato](report-template.md), incluído automaticamente no pacote distribuído.

## Etapas da investigação

1. **Prever:** desenhe fonte → pré-processado → assembly → object file → executável → processo. Preveja quais referências estarão indefinidas antes do linking.
2. **Observar:** execute `make` e `make observe` nos materiais. Anote excertos de `.i`, `.s`, símbolos, relocations, headers ELF, maps e trace. Separe resultado observado de previsão.
3. **Explicar:** preencha a tabela de responsabilidades do roteiro. Relacione um segmento `LOAD` com um mapping usando offset e permissões; não iguale endereço virtual e offset de arquivo. Explique a diferença entre `printf` e a syscall de escrita observada.
4. **Implementar:** acrescente uma segunda função em `operations.c`, declare-a no header e use-a em `main.c`, preservando a saída contratada. Reconstrua os estágios e anote quais símbolos e relocations mudaram. Não se exige implementar compilador, linker ou loader.
5. **Verificar:** execute `make check`. Explique por que compilar isoladamente teve sucesso antes dos erros de linking.

## Critérios de conclusão

Entregue os dois módulos, comandos reproduzíveis e uma tabela com cinco classes de artefatos: fonte, pré-processado, assembly, object file e executável. Anexe excertos anotados de símbolos, relocations, seções, segmentos, maps e strace. Entregue a linha do tempo e uma tabela que distingue compilador, montador, linker, kernel e dynamic loader. Registre os dois erros de linking, a mudança de função e os checks.

Checks aprovados confirmam o material auxiliar; não avaliam a explicação nem substituem trace ausente.

## Extensões opcionais

Compare `-fPIE -pie` com `-fno-pie -no-pie` em diretórios distintos. Compare duas execuções e relacione ELF, PIE e ASLR sem exigir que endereços mudem. Explore PLT/GOT, otimização ou static linking, declarando dependências e diferenças de ambiente.

## Participação no clube

Compartilhe hipótese, comando, trecho observado e explicação. Informe versões, flags e limitações. Ao revisar um relato, confira a distinção entre evidência, inferência e responsabilidade de cada componente.

## Referências e atividades relacionadas

Leia as [referências orientadas](references.md) após observar os artefatos. Engenharia reversa aprofunda disassembly; processos e pipes ajudam a interpretar execução e file descriptors. ABI e dynamic linking ampliam o estudo de símbolos e bibliotecas.

`make observe` exige strace ≥ 6.6 para `--kill-on-exit`. O arquivo `strace.txt` é filtrado a `execve`, `openat`, `mmap`, `mprotect`, `read`, `write` e `exit_group`; não é o histórico completo de syscalls. O filtro destaca carregamento, memória e I/O.
