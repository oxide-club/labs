---
title: Laboratório de Segurança de Memória
area: memory
slug: 003-memory-safety-lab
summary: Compare views, cópias e reset lógico para investigar validade de acesso e limites do AddressSanitizer.
question: Um endereço ainda acessível e uma execução sem diagnóstico tornam uma referência válida?
draft: false
publishedAt: 2026-10-25
updatedAt: 2026-10-25
topics: [Memória, C, Lifetime, Ownership, Sanitizadores]
prerequisites: [malloc e free, Pointers e strings, Leitura de stack traces]
tools: [Compilador C11, AddressSanitizer, Python 3]
environment: Linux com GCC ou Clang e runtime AddressSanitizer e LeakSanitizer
difficulty: intermediate
relatedChallenges: [016-use-after-free, 017-arena]
---

## O que vamos investigar

Uma view guarda um endereço dentro de outro objeto; uma cópia independente possui
outra alocação. Ambas podem mostrar o mesmo texto antes da destruição do original,
mas têm condições diferentes de validade. Além disso, um contrato pode invalidar
uma referência sem devolver a região ao alocador.

Você vai comparar **quatro cenários completos**, com uma hipótese sobre cada um:

| Cenário | Condição que muda | Questão |
| --- | --- | --- |
| `borrowed` | Leitura da view antes de free. | Qual lifetime autoriza esse acesso? |
| `owner-null` | Free seguido de owner igual a NULL; a view não é atualizada. | Zerar um pointer protege os aliases? |
| `copy` | Cópia independente criada antes de free. | O que a cópia preserva e quem deve liberá-la? |
| `reset` | A região continua alocada, mas muda sua geração lógica. | ASan conhece a validade definida pelo contrato da arena? |

O objetivo não é corrigir quatro programas. Eles são instrumentos para distinguir
**validade na linguagem, validade no contrato e presença de um diagnóstico**.
O desafio de use-after-free já trabalha diagnóstico e correção. Aqui, a entrega
central é explicar o alcance das evidências e comparar modelos de ownership.

### O modelo de reset

O caso `reset` modela uma região cujo contrato permite usar um handle somente
quando sua geração coincide com a geração atual. O reset incrementa a geração
e reutiliza os mesmos bytes para outra mensagem. Ele não chama free.

O instrumento lê deliberadamente a view antiga para mostrar o limite da detecção.
Essa leitura permanece dentro de uma alocação viva e é válida pelas regras de C,
mas não atende ao contrato lógico do handle. Não é um allocator completo nem um
exemplo de uso correto da API de uma arena. Não extrapole esse caso para acesso após free.

## Antes de começar

### Linguagens e ambiente

O núcleo usa C11, Python 3 e ASan/LSan em Linux. C++ ou Rust podem complementar a
comparação de ownership; não substituem a observação do código C.
Leia o [guia dos materiais](materials/README.md). Registre compilador, sistema,
flags e opções do sanitizador. Não há bibliotecas Python externas.

O cenário `owner-null` contém um defeito intencional. Execute-o somente pelo runner
com ASan, em processo separado e com timeout. Não use a saída de uma execução com
comportamento indefinido como oráculo de bytes nem como demonstração de validade.

## Materiais

- [lifetimes.c](materials/experiments/lifetimes.c): quatro cenários completos.
- [compare.py](materials/experiments/compare.py): compilação e coleta isolada de logs.
- [Guia de execução](materials/README.md) e [modelo de relato](report-template.md).
- [Contrato histórico opcional](materials/legacy.md): correção de lifetime e CLI de offsets.

Não é necessário completar `starter/lifetime.c` ou `starter/variation.c` para
executar ou concluir a investigação atual. A CLI histórica é uma extensão.

## Etapas da investigação

### 1. Formular hipóteses

Antes de executar, desenhe as alocações, owner, view e cópia em cada cenário.
Registre se a leitura atende às regras de C e ao contrato lógico, separadamente.
Preveja onde ASan deve emitir um diagnóstico e justifique a previsão.

Confronte explicitamente estas hipóteses: “zerar o owner atualiza todos os aliases”
e “não receber diagnóstico demonstra que o handle ainda é válido”. Escreva qual
observação poderia refutar cada uma. Não preveja um texto específico para a leitura após free.

### 2. Coletar evidências

Execute `compare.py` com um diretório novo. Preserve `results.json`, stdout e stderr
de todos os processos, os logs de compilação e suas previsões originais.
O status zero do runner significa que a coleta encontrou as observações esperadas;
não significa que todos os programas filhos terminaram com sucesso.

Para `owner-null`, localize alocação, liberação e acesso no diagnóstico. Relacione
cada ponto ao desenho. Não use endereços literais como critério entre execuções.
Para os controles, registre status e ausência ou presença de diagnóstico.

### 3. Comparar mecanismos

Compare `borrowed` e `owner-null`: a alteração relevante é a ordem entre acesso
e destruição. Explique por que atribuir NULL ao owner não reescreve a variável view.

Compare `owner-null` e `copy`: identifique a alocação adicional e sua responsabilidade
de liberação. Explique por que copiar apenas o pointer não produziria o mesmo efeito.

Compare `owner-null` e `reset`: no primeiro, terminou o lifetime da alocação;
no segundo, mudou um contrato lógico sobre uma região ainda viva. Identifique o
contraexemplo à hipótese de que ausência de diagnóstico garante validade de uso.

### 4. Implementar uma intervenção discriminante

Crie uma cópia de `lifetimes.c`. No cenário `copy`, depois de copiar e antes de
liberar o original, substitua `Club` por `Rust` na região original. Acrescente uma
observação da view enquanto o original ainda está vivo e preserve a impressão
da cópia depois do descarte. Preveja as duas saídas antes de executar.

Compile essa cópia com ASan/LSan conforme o guia e execute somente `copy`.
Entregue o patch, logs e a explicação de como o experimento distingue alias de cópia.
Os checks da coleta original não devem ser alterados para aceitar sua saída ampliada.

Em outra cópia, impeça a leitura da view antiga de `reset` quando as gerações
forem diferentes. Registre a rejeição e explique por que essa checagem pertence à
API, e não ao ASan. Preserve a liberação da região. A intervenção é pequena;
não é necessário construir uma arena ou uma CLI de offsets.

### 5. Explicar limites

Classifique cada afirmação do relato como observação, regra de C ou regra do
contrato. Uma execução sem diagnóstico não prova ausência geral de UB ou leaks.
A ausência do diagnóstico esperado em `owner-null` é coleta inconclusiva, não
refutação das regras de lifetime. Falha do runtime também não é resultado válido.

Se a previsão estava correta, registre a hipótese alternativa que os dados
rejeitam; não é necessário inventar uma previsão errada.

## Critérios de conclusão

Entregue a matriz dos quatro cenários, desenhos, previsões, comandos e logs.
A matriz deve distinguir validade em C, validade lógica e diagnóstico observado.
Explique as três pilhas do UAF, a independência da cópia e o reset sem free.
Inclua os dois patches instrumentais e suas evidências: mutação do original após
copiar e rejeição de handle de geração antiga.

Todos os controles devem terminar sem diagnóstico de memória ou leak. O UAF deve
ser identificado pelo sanitizador. Se o ambiente impedir essa coleta, registre a
pendência e execute em um Linux compatível antes de declarar conclusão prática.

Passar em testes de uma correção ou mostrar `Club` não basta. A conclusão deve
explicar por que os cenários têm garantias diferentes apesar de usarem endereços
e mensagens semelhantes.

## Extensões opcionais

Faça a correção histórica e a CLI de offsets do [guia anterior](materials/legacy.md),
com seus checks próprios. Compare também borrowing em Rust ou ownership em C++.
Investigue outro defeito somente com mecanismo e instrumento apropriados; ASan
não é um detector geral de leitura não inicializada.

## Participação no clube

Compartilhe uma hipótese, a comparação que a testa e trechos anotados dos logs.
Mostre onde termina uma garantia de linguagem e começa uma regra da aplicação.
Use o [modelo de relato](report-template.md) e remova caminhos pessoais dos logs compartilhados.

## Referências e atividades relacionadas

As [referências](references.md) apoiam lifetime e instrumentação. O desafio 016
se concentra em diagnosticar e corrigir uma cópia inválida. O desafio 017 constrói
uma arena. Este laboratório usa comparações menores para investigar limites das evidências.
