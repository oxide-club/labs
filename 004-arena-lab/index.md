---
title: Laboratório de Alocação de Memória
area: memory
slug: 004-arena-lab
summary: Implemente uma arena com alignment correto e explique limites, falhas e reset.
question: Como distribuir uma região limitada preservando alignment, limites e estado?
draft: false
supersededBy: 017-arena
publishedAt: 2026-10-25
updatedAt: 2026-10-25
topics: [Memória, Alocação, C]
prerequisites: [Pointers, size_t, malloc e free, Unsigned overflow]
tools: [Compilador C11, GNU ld]
environment: Linux; C11; região obtida por malloc
difficulty: intermediate
---

## O que vamos investigar

Esta atividade foi consolidada no [desafio 017-arena](https://oxideclub.dev/desafios/017-arena/).
O roteiro abaixo permanece como material histórico. Para iniciar ou continuar, use o desafio;
não é necessário implementar os dois contratos.


### O que você vai construir

Você vai **implementar um allocator que distribui partes de uma região de memória
reservada de uma só vez**. Essa região é a arena. Ela mantém uma capacidade total
e um marcador `used`, que indica quanto espaço já foi consumido.

Por exemplo, numa arena de 64 bytes, os pedidos `(size=3, alignment=1)` e
`(size=5, alignment=1)` ocupam os offsets 0 e 3; ao final, `used` vale 8.
Se o próximo pedido exigir um início que respeite o alignment, pode ser necessário deixar espaço
entre os blocos. Esse espaço, chamado padding, também conta em `used`.

| Função de `arena.c` | Responsabilidade |
| --- | --- |
| `arena_init` | Reservar a região e iniciar o estado. |
| `arena_alloc` | Encontrar espaço com o alignment solicitado e avançar `used` somente em sucesso. |
| `arena_reset` | Permitir reutilizar toda a região; referências anteriores deixam de valer pelo contrato. |
| `arena_destroy` | Fazer dealocação da região e zerar o estado. |

Complete `materials/starter/arena.c`. A entrega reúne implementação, testes e
um desenho dos blocos e do padding, com o estado antes e depois dos pedidos.
Uma falha de alocação deve deixar a arena disponível para pedidos posteriores.

### Conceitos para a investigação

Uma arena reserva uma região de memória e distribui blocos em sequência. O padding é o espaço
entre o fim de um bloco e o início do próximo que respeita o alignment. Esse espaço também consome
capacidade. Como garantir que blocos vivos não se sobreponham e que uma falha não
consuma espaço?

#### Contrato técnico

Implemente exatamente a API de `materials/starter/arena.h`. `a` deve ser um pointer
válido em todas as operações. `arena_init` recebe uma struct zerada; não
reinicialize uma arena viva. Capacidade zero ou falha de `malloc` retorna `false`
e mantém a struct zerada. O sucesso reserva a região, define `capacity` e
mantém `used=0`.

`arena_alloc` exige arena inicializada. Aceite alignments que sejam potências
de dois entre 1 e `_Alignof(max_align_t)`, inclusive. Se `size` for zero, o
alignment for inválido, não houver espaço ou houver overflow no cálculo, retorne
`NULL` sem alterar `used`. Verifique espaço e overflow antes de somas perigosas
ou de formar pointers. Após sucesso, `used` inclui padding e tamanho solicitado;
`0 <= used <= capacity`. Blocos vivos não se sobrepõem. Não há dealocação individual.

`arena_reset` define `used=0` e conserva região e capacidade. As referências
anteriores deixam de ser utilizáveis pelo contrato, mesmo que os bytes ainda
existam. Não é obrigatório apagá-los. `arena_destroy` faz dealocação da região e zera os
três campos; repeti-lo é permitido. Reset e destruição aceitam struct zerada.
A API não fornece sincronização entre threads.

A base de `malloc` atende aos alignments fundamentais. Escreva objetos pelo
tipo apropriado: alignment e tipo efetivo são questões distintas. Não substitua
a região por um array declarado de `char` para justificar acesso por outro tipo.

## Antes de começar

### Linguagens e ambiente

A implementação de referência usa **C11**. Você pode usar outra linguagem que
permita gerenciamento explícito de memória, como Rust ou C++, ambas recomendadas.
Trabalhe com uma região real de memória e implemente sua própria política de
alocação, respeitando alignment, pointers e lifetime dos objetos.

Os materiais fornecem código inicial em C11. Outras linguagens são aceitas com
adaptação do contrato, conforme o guia abaixo.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Conheça `size_t`, `SIZE_MAX`, `sizeof`, `_Alignof`, pointers e unsigned overflow.
Use Linux com compilador C11; o check de falha de alocação usa `--wrap` do GNU ld.
Consulte os comandos completos em [materials/README.md](materials/README.md).
Trabalhe sobre uma cópia do starter e preserve os checks públicos.

## Materiais

[O guia de materiais](materials/README.md) descreve o starter incompleto,
os checks, o CSV de pedidos e o experimento independente de layout.
[As referências](references.md) apresentam dois allocators reais com perguntas
de leitura. O modelo compartilhado de relato acompanha o pacote como
`report-template.md`; no repositório, consulte [o modelo](report-template.md).

## Etapas da investigação

1. **Prever:** registre os offsets e `used` de `(3,1)` e `(5,1)` em 64 bytes.
   Preveja um pedido de 64 seguido de 1 e explique qual estado a falha preserva.
2. **Observar:** execute `layout.c`. Registre tamanho e alignment de `long double`.
   Preveja seu offset após reservar um byte, sem fixar valores de outra máquina.
3. **Explicar:** desenhe blocos e padding. Justifique por que verificar somente
   o resultado de uma soma que já sofreu overflow não basta. Distinga reset de destruição.
4. **Implementar:** complete `arena.c`, mantendo API e contrato. Registre as condições
   que garantem ausência de sobreposição e preservação do estado em falhas.
5. **Verificar:** compile e execute os dois checks. Registre retornos, offsets e
   resultados; acrescente um caso próprio de fronteira. O starter deve falhar no
   check principal. Uma compilação bem-sucedida não encerra o laboratório.

## Critérios de conclusão

Entregue `arena.h`, `arena.c`, testes e relato com previsões, comandos, rastro de
alocações e explicação dos invariantes. Os checks devem passar após sua implementação,
incluindo continuidade, escrita/leitura de `1.25L`, limite exato, `SIZE_MAX`, falha
seguida de sucesso, padding, reset e destruição repetida. Use apenas pointers
novos após reset. Explique as limitações dos testes: os casos não provam correção geral.

## Extensões opcionais

Crie um pool separado com `pool_init`, `pool_destroy`, `pool_alloc`, `pool_free`
e `pool_stats`. Use first-fit em ordem de endereço, split e coalescing; metadados
contam na capacidade e resultados respeitam `_Alignof(max_align_t)`. Defina o
bloco mínimo antes dos testes. `pool_free(NULL)` não faz nada; outros argumentos
são pointers vivos do mesmo pool. Detecção de pointers arbitrários e dupla
dealocação fica fora desse contrato. Verifique reutilização do bloco central,
um único bloco livre ao fazer dealocação de todos e diferença entre memória livre total e
maior pedido possível. A extensão não bloqueia a conclusão da arena.

## Participação no clube

Compartilhe previsão, tentativa, comando de reprodução e resultado observado.
Ao perguntar, identifique o primeiro pedido que diverge do previsto e o estado
antes/depois. Compare explicações dos invariantes sem publicar uma solução central.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md). Representação binária ajuda a
entender metadados; segurança de memória aprofunda lifetime; cache e locality
permitem investigar o efeito de percursos sobre os blocos reservados.
