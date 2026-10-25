---
title: Laboratório de Isolamento de Processos
area: operating-systems
slug: 016-isolation-lab
summary: Construa um supervisor limitado e investigue recursos, namespaces e políticas de syscalls em VM descartável.
question: Quais propriedades distinguem supervisão, limites de recursos e isolamento de segurança?
draft: false
publishedAt: 2026-10-25
topics: [Processos, Isolamento, Recursos]
prerequisites: [C, fork e exec, Sinais, File descriptors]
tools: [Compilador C11, Make, Python 3, VM descartável]
environment: Linux em VM descartável com usuário sem privilégios e procfs
difficulty: advanced
---

## O que vamos investigar

### O que você vai construir e investigar

Você vai **implementar um supervisor que inicia um programa, aplica limites e
acompanha seu término**, e depois comparar supervisão com mecanismos de isolamento.
Complete `materials/supervisor.c`.

```text
supervisor → filho principal → possível descendente benigno
     └→ controla prazo, encerra o grupo próprio e faz reaping
```

Se o programa principal terminar com status 7 dentro do prazo, o supervisor deve
preservar esse status depois de limpar os descendentes. Se o prazo vencer antes
do término observado, deve encerrar o grupo, fazer reaping dos filhos e retornar 124.
Enviar um sinal e fazer reaping são responsabilidades diferentes.

**Execute supervisor, fixtures e checks dinâmicos somente na VM descartável
exigida abaixo.** Sem VM, é possível compilar e concluir o percurso teórico,
registrando a verificação prática como pendente.

A entrega prática reúne o supervisor, evidências dos checks, uma árvore de
processos explicada e uma tabela de recursos e restrições de namespaces, cgroups
e seccomp. Essa comparação deve mostrar quais propriedades cada mecanismo oferece;
o supervisor sozinho não estabelece uma fronteira completa de isolamento.

### Conceitos para a investigação

Um supervisor acompanha processos e encerra trabalho que excede um prazo. Um limite
de recursos restringe consumo. Uma fronteira de isolamento restringe acesso a objetos
e operações. Vamos construir o primeiro e investigar como os outros dois diferem.

#### Contrato técnico

Implemente [supervisor.c](materials/supervisor.c) conforme o [contrato completo](materials/contract.md).
A interface de linha de comando (CLI) recebe um prazo de 100 a 5000 ms,
o caminho do executável e seus argumentos. O supervisor aplica limites
ao filho, preserva seu status, encerra a árvore de processos benignos que criou e faz reaping deles.
O contrato especifica erros, file descriptors, sinais, adoção de órfãos e limpeza após falhas.
A solução didática **não é adequada para execução de código adversarial em produção**
sem arquitetura, revisão e isolamento adicionais.

## Antes de começar

### Linguagens e ambiente

A implementação de referência usa **C11**. Outras linguagens com acesso às APIs
Linux são aceitas; Rust, Go e Python são alternativas recomendadas. Execute os
experimentos em uma VM Linux descartável, sem privilégios, mantendo todas as
restrições do roteiro.

Os materiais fornecem código inicial em C11. Outras linguagens são aceitas com
adaptação do contrato, conforme o guia abaixo.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Conheça `fork`, `exec`, `waitpid`, sinais, grupos de processos e file descriptors.
Use uma VM Linux descartável, sem segredos, pastas do host compartilhadas ou
credenciais de serviços. Registre imagem, kernel e snapshot; trabalhe sem privilégios.
O [guia de materiais](materials/README.md) separa compilação estática e execução na VM.
Um container não substitui a VM exigida neste roteiro.

Se não houver VM, faça o [percurso teórico](experiments/theory.md) e compile os fontes.
Não execute supervisor, fixtures ou experiências no host. A variável de confirmação
é uma declaração humana, não uma prova de que o ambiente é uma VM.

## Materiais

O [guia](materials/README.md) lista o starter incompleto, alvos benignos com duração
limitada, Makefile e [checks públicos](checks/check.py). O [roteiro de experiências](experiments/README.md)
orienta a comparação de mecanismos; o [inventário](experiments/observe.py) só lê o ambiente.
Use o [modelo de relatório](report-template.md) e as [leituras orientadas](references.md).

## Etapas da investigação

1. **Prever:** desenhe a árvore principal/filho e preveja status para saída 7, sinal,
   timeout, reserva de memória recusada e arquivo sem permissão. Diferencie o tempo de CPU do wall-clock time.
2. **Observar:** na VM, compile e execute apenas as fixtures descritas no guia. Registre
   status e limites. O starter retorna 125; isso ainda não verifica supervisão.
3. **Explicar:** identifique quem executa reaping de um descendente após a saída do pai. Explique
   por que enviar um sinal não equivale a executar reaping e por que um grupo não é uma sandbox.
4. **Implementar:** complete o supervisor. Justifique a sincronização da preparação e
   a limpeza em todos os caminhos de falha, inclusive depois do primeiro fork.
5. **Verificar:** rode os checks somente na VM; registre comandos e resultados. Revise
   também falhas parciais e sinais recebidos pelo supervisor, ausentes dos checks automáticos.
6. **Investigar:** complete a tabela de recursos/restrições do roteiro para namespaces,
   cgroups e seccomp. Registre permissões e recorra ao percurso teórico para mecanismos
   indisponíveis. Separe cada propriedade observada das hipóteses e garantias justificadas.

## Critérios de conclusão

Entregue supervisor, resultados dos checks, justificativa de reaping e tabela de
mecanismos. Inclua ameaça, file descriptors herdados, privilégios, acesso a arquivos/rede e
limitações. A conclusão prática exige execução na VM. O percurso teórico tem critérios
próprios e pode ser concluído sem VM; ele não comprova runtime nem substitui essa pendência.

## Extensões opcionais

Depois de concluir as etapas obrigatórias, investigue filesystem restrito, UID/GID, rede isolada e políticas
seccomp específicas. Compare container, VM e WebAssembly por propriedades explícitas.
Mantenha os alvos benignos e a VM descartável; não amplie silenciosamente o modelo de ameaça.

## Participação no clube

Compartilhe a previsão, a árvore de processos, um caso reproduzível e uma pergunta
concreta. Informe se o resultado veio da VM, de análise estática ou de estudo teórico.
Não publique tokens, caminhos pessoais ou conteúdo de arquivos do host.

## Referências e atividades relacionadas

Consulte as [referências](references.md) após fixar suas hipóteses. Processos e Pipes,
Syscalls e Segurança de Memória ajudam a interpretar os mecanismos. O número 016 é
o identificador do pacote; o tema corresponde à seção 14 do currículo.
