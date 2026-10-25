---
title: Laboratório de Processos e Pipes
area: operating-systems
slug: 006-processes-lab
summary: Implemente um executor POSIX e um pipeline de dois comandos.
question: Como criar processos, conectar file descriptors e observar seu término?
draft: false
publishedAt: 2026-10-25
topics: [Processos, Pipes, POSIX]
prerequisites: [C, argc/argv, File descriptors]
tools: [cc, Python 3, strace]
environment: Linux x86-64 e interfaces POSIX; C11
difficulty: intermediate
---

## O que vamos investigar

Um processo possui uma imagem de execução e file descriptors. `fork` cria um filho; `execvp` substitui a imagem do processo que o chama. Um pipe conecta um escritor a um leitor. Investigue como cópias de file descriptors afetam o EOF, isto é, a indicação de fim dos dados.

### Contrato técnico

Implemente exatamente estas interfaces:

```text
./oxrun run -- programa argumento...
./oxrun pipe -- programa1 argumento... ::: programa2 argumento...
```

A shell host já processou suas aspas. Preserve os elementos de `argv`, inclusive argumentos vazios e argumentos com espaços. `oxrun` não interpreta uma linguagem de comandos. No modo `pipe`, o token `:::` deve aparecer exatamente uma vez, com um comando de cada lado. Esse token não pode ser um argumento literal nesse modo. Em `run`, pode ser um argumento comum.

Use `fork`, `execvp` e `waitpid`; no pipeline, acrescente `pipe`, `dup2` e `close`. Não use `system`, `popen` ou uma shell para executar o núcleo. Conecte stdout da esquerda a stdin da direita. Preserve stderr herdado; envie diagnósticos próprios a stderr.

| Condição | Status exigido |
| --- | --- |
| `run`, término normal | Status do filho |
| `pipe`, término normal | Status do comando da direita |
| Comando termina por sinal | `128 + número do sinal` |
| `execvp` falha com `ENOENT` | 127 |
| Outra falha de `execvp` | 126 |
| Uso inválido ou falha interna de preparação | 2 e diagnóstico |

Valide todo o uso antes de iniciar processos. Espere todos os filhos diretos criados, mesmo quando o status solicitado já estiver disponível. Retome `waitpid` após `EINTR`. Inicie os dois lados antes de esperar seu término. Feche cópias desnecessárias para permitir EOF. Se a preparação falhar após criar um filho, feche os file descriptors, encerre os filhos diretos próprios e execute o reaping deles antes de retornar 2. Essa recuperação pode usar `SIGKILL`. Os casos obrigatórios não criam descendentes adicionais.

## Antes de começar

### Linguagens e ambiente

Referência: **C11**. Aceitas: Livre entre implementações POSIX equivalentes; por exemplo C, Rust e Python.
Recomendadas: Rust e Python. POSIX; referência Linux x86-64; fork, exec, pipes, descritores e reaping explícitos.
Materiais oficiais: C11 existente.
Equivalência: equivalente ao núcleo.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

Use Linux x86-64, compilador C11, Make, Python 3 e os comandos `printf`, `wc`, `dd`, `true`, `cat` disponíveis pelo `PATH`. `strace` é recomendado para investigar espera e fechamento. Leia o [guia dos materiais](materials/README.md) e compile o starter. Ele retorna 2 e ainda não executa comandos.

## Materiais

O [README](README.md) apresenta a entrada rápida. Em `materials/`, há `starter/oxrun.c`, o `starter/probe.c` original do Anexo A, checks públicos, fixtures e um roteiro de experimentos. Consulte as [referências orientadas](references.md). Use o [modelo de relatório](report-template.md) no repositório ou registre as evidências descritas no guia do pacote.

## Etapas da investigação

1. **Prever:** preencha a tabela de file descriptors do [roteiro](materials/experiments/descriptors.md). Preveja status, stdout e condição de EOF para cada caso.
2. **Observar:** execute `probe` diretamente. Registre 7 e 143 separadamente da saída. Observe um processo com `strace -f` quando disponível.
3. **Explicar:** descreva por que esperar o produtor antes de iniciar o consumidor pode bloquear. Explique por que um escritor herdado pode impedir EOF.
4. **Implementar:** complete `run`, depois `pipe`. Registre invariantes de ownership dos file descriptors, PIDs e recuperação de preparação.
5. **Verificar:** execute `make check` nos materiais. Compare stdout e status separadamente. Registre checks e revisão de reaping, inclusive suas limitações.

## Critérios de conclusão

Entregue código, comandos de compilação, resultados, tabela de file descriptors e explicação dos invariantes. Os checks devem passar para argumentos com espaços, 7, 143, 127, 126, EOF, 1 MiB, status da direita e uso inválido. Justifique que cada filho criado tem uma espera correspondente. Revise a recuperação parcial e `EINTR`; os checks públicos não demonstram esses caminhos raros por si sós.

## Extensões opcionais

Defina outro contrato antes de adicionar parser, redirecionamentos `<`/`>`, mais estágios ou shell interativa. Job control, foreground/background, grupos de processos e controle de terminal são aprofundamentos separados. A sessão usada pelos checks serve apenas para limitar a limpeza dos testes.

## Participação no clube

Compartilhe uma hipótese, o comando reproduzível e o resultado observado. Informe ambiente e limitações. Ao revisar uma tentativa, confira ownership de file descriptors e reaping, além do status final.

## Referências e atividades relacionadas

Leia [references.md](references.md) para Process API, semântica de pipes e leitura de BusyBox. Compilação e execução ajudam a entender `exec`; concorrência amplia o estudo do progresso simultâneo. Isolamento de processos exige outro ambiente e outro contrato.
