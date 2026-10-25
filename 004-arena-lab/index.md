---
title: Laboratório de Memory Allocation
slug: 004-arena-lab
summary: Implemente uma arena alinhada e explique limites, falhas e reset.
question: Como distribuir uma região limitada preservando alinhamento, limites e estado?
draft: false
publishedAt: 2026-10-25
topics: [Memória, Allocation, C]
prerequisites: [Ponteiros, size_t, malloc e free, Overflow sem sinal]
tools: [Compilador C11, GNU ld]
environment: Linux; C11; região obtida por malloc
difficulty: intermediate
---

## O que vamos investigar

Uma arena reserva uma região e distribui blocos sequenciais. O padding é o espaço
entre o fim de um bloco e o início alinhado do próximo. Esse espaço também consome
capacidade. Como garantir que blocos vivos não se sobreponham e que uma falha não
consuma espaço?

### Contrato técnico

Implemente exatamente a API de `materials/starter/arena.h`. `a` deve ser um ponteiro
válido em todas as operações. `arena_init` recebe uma estrutura zerada; não
reinicialize uma arena viva. Capacidade zero ou falha de `malloc` retorna `false`
e mantém a estrutura zerada. O sucesso reserva a região, define `capacity` e
mantém `used=0`.

`arena_alloc` exige arena inicializada. Aceite alinhamentos que sejam potências
de dois entre 1 e `_Alignof(max_align_t)`, inclusive. Se `size` for zero, o
alinhamento for inválido, não houver espaço ou o cálculo transbordar, retorne
`NULL` sem alterar `used`. Verifique espaço e overflow antes de somas perigosas
ou de formar ponteiros. Após sucesso, `used` inclui padding e tamanho solicitado;
`0 <= used <= capacity`. Blocos vivos não se sobrepõem. Não há liberação individual.

`arena_reset` define `used=0` e conserva região e capacidade. As referências
anteriores deixam de ser utilizáveis pelo contrato, mesmo que os bytes ainda
existam. Não é obrigatório apagá-los. `arena_destroy` libera a região e zera os
três campos; repeti-lo é permitido. Reset e destruição aceitam estrutura zerada.
A API não fornece sincronização entre threads.

A base de `malloc` atende aos alinhamentos fundamentais. Escreva objetos pelo
tipo apropriado: alinhamento e tipo efetivo são questões distintas. Não substitua
a região por um array declarado de `char` para justificar acesso por outro tipo.

## Antes de começar

### Linguagens e ambiente

Referência: **C11**. Aceitas: Livre sob gerenciamento explícito; por exemplo C, Rust e C++.
Recomendadas: Rust e C++. Região real, alinhamento, ponteiros, lifetime e política própria de allocation.
Materiais oficiais: C11 existente.
Equivalência: equivalente sob contrato adaptado.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

Conheça `size_t`, `SIZE_MAX`, `sizeof`, `_Alignof`, ponteiros e overflow sem sinal.
Use Linux com compilador C11; o check de falha de allocation usa `--wrap` do GNU ld.
Consulte os comandos completos em [materials/README.md](materials/README.md).
Trabalhe sobre uma cópia do starter e preserve os checks públicos.

## Materiais

[O guia de materiais](materials/README.md) descreve o starter incompleto,
os checks, o CSV de pedidos e o experimento independente de layout.
[As referências](references.md) apresentam dois alocadores reais com perguntas
de leitura. O modelo compartilhado de relato acompanha o pacote como
`report-template.md`; no repositório, consulte [o modelo](report-template.md).

## Etapas da investigação

1. **Prever:** registre os offsets e `used` de `(3,1)` e `(5,1)` em 64 bytes.
   Preveja um pedido de 64 seguido de 1 e explique qual estado a falha preserva.
2. **Observar:** execute `layout.c`. Registre tamanho e alinhamento de `long double`.
   Preveja seu offset após reservar um byte, sem fixar valores de outra máquina.
3. **Explicar:** desenhe blocos e padding. Justifique por que verificar somente
   o resultado de uma soma que já transbordou não basta. Distinga reset de destruição.
4. **Implementar:** complete `arena.c`, mantendo API e contrato. Registre as condições
   que garantem ausência de overlap e preservação do estado em falhas.
5. **Verificar:** compile e execute os dois checks. Registre retornos, offsets e
   resultados; acrescente um caso próprio de fronteira. O starter deve falhar no
   check principal. Uma compilação bem-sucedida não encerra o laboratório.

## Critérios de conclusão

Entregue `arena.h`, `arena.c`, testes e relato com previsões, comandos, rastro de
allocations e explicação dos invariantes. Os checks devem passar após sua implementação,
incluindo continuidade, escrita/leitura de `1.25L`, limite exato, `SIZE_MAX`, falha
seguida de sucesso, padding, reset e destruição repetida. Use apenas ponteiros
novos após reset. Explique as limitações dos testes: os casos não provam correção geral.

## Extensões opcionais

Crie um pool separado com `pool_init`, `pool_destroy`, `pool_alloc`, `pool_free`
e `pool_stats`. Use first-fit em ordem de endereço, split e coalescing; metadados
contam na capacidade e resultados respeitam `_Alignof(max_align_t)`. Defina o
bloco mínimo antes dos testes. `pool_free(NULL)` não faz nada; outros argumentos
são ponteiros vivos do mesmo pool. Detecção de ponteiros arbitrários e dupla
liberação fica fora desse contrato. Verifique reutilização do bloco central,
um único bloco livre ao liberar todos e diferença entre memória livre total e
maior pedido possível. A extensão não bloqueia a conclusão da arena.

## Participação no clube

Compartilhe previsão, tentativa, comando de reprodução e resultado observado.
Ao perguntar, identifique o primeiro pedido que diverge do previsto e o estado
antes/depois. Compare explicações dos invariantes sem publicar uma solução central.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md). Representação binária ajuda a
entender metadados; segurança de memória aprofunda lifetime; cache e localidade
permite investigar o efeito de percursos sobre os blocos reservados.
