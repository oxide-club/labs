---
title: Laboratório de Segurança de Memória
area: memory
slug: 003-memory-safety-lab
summary: Diagnostique um use-after-free e corrija o lifetime sem causar memory leak.
question: Quando um ponteiro deixa de permitir acesso aos dados?
draft: false
publishedAt: 2026-10-25
topics: [Memória, C, Lifetime]
prerequisites: [malloc e free, Ponteiros e strings, Leitura de stack traces]
tools: [Compilador C11, AddressSanitizer, Python 3]
environment: Linux x86-64 com GCC ou Clang e runtime AddressSanitizer
difficulty: intermediate
---

## O que vamos investigar

Guardar o endereço de um objeto em um ponteiro não prolonga seu tempo de vida
(lifetime), isto é, o intervalo em que ele existe segundo o modelo da linguagem.
Um *use-after-free* ocorre quando o programa acessa um bloco depois de liberá-lo.
Você vai usar o AddressSanitizer (ASan) para relacionar a alocação, a liberação e
o acesso inválido. Depois, vai corrigir a causa sem introduzir um vazamento de memória.

### Contrato técnico

O arquivo `materials/starter/lifetime.c` contém o programa original `vida.c`.
Ele aloca `"Oxide Club"` e cria uma visão a partir do deslocamento (offset) 6, ou
seja, um ponteiro para uma posição dentro do mesmo bloco. Em seguida,
libera a mensagem e tenta ler a visão. O defeito inicial é intencional.
Corrija esse arquivo mantendo `Club\n` em stdout, status 0 e uma única liberação
do bloco. Se `malloc` falhar, preserve o status 2. Todos os acessos devem ocorrer
durante o lifetime do bloco. Não remova a allocation nem substitua a mensagem por
uma string estática para contornar a investigação.

Depois, implemente `materials/starter/variation.c`. Sua interface de linha de
comando (CLI) é `variation DESLOCAMENTO`.
Aceite exatamente um argumento não vazio com dígitos ASCII de `0` a `9`, sem
sinal nem espaços, cujo valor esteja entre 0 e 10. Zeros à esquerda são aceitos.
Rejeite valores maiores sem overflow na conversão. Valide antes de formar a
visão, inclusive antes de formar o ponteiro no offset 11. Embora seja
possível formar um ponteiro one-past para este bloco de 11 bytes, ele não é uma
visão de string válida; o contrato exige a rejeição antes dessa formação.

| Entrada | stdout exata | Status |
| --- | --- | ---: |
| `0` | `Oxide Club\n` | 0 |
| `6` | `Club\n` | 0 |
| `10` | `\n` | 0 |
| `11`, argumento inválido ou quantidade incorreta | vazia | 2 |

Em sucesso, stderr fica vazia. Em erro de argumento, stderr deve conter exatamente
`Erro: use um deslocamento decimal entre 0 e 10.\n`. Em falha de allocation, retorne
2, não escreva em stdout e libere qualquer recurso já adquirido; a mensagem em
stderr não é fixada. Mantenha allocation dinâmica, cópia dos 11 bytes e uma única
liberação em cada execução bem-sucedida. A visão toma emprestado o acesso ao bloco (borrowing): ela não é uma segunda
alocação e não deve ser passada a `free`. Os checks não simulam falta de memória;
explique esse caminho na revisão do código.

## Antes de começar

### Linguagens e ambiente

A parte obrigatória usa **C11 e AddressSanitizer** para observar a alocação, a liberação e o
acesso inválido. Os materiais fornecem código em C11.

C++ e Rust são recomendados para comparações. Essas comparações complementam a
investigação do defeito em C, mas não a substituem.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Conheça `malloc`, `free`, arrays, strings terminadas em zero e aritmética de
ponteiros. Instale Python 3 e GCC ou Clang com runtime ASan. Linux x86-64 é o
ambiente de referência; GDB é opcional. Leia [o guia local](README.md) e
[o guia dos materiais](materials/README.md). Os comandos não precisam de root.

## Materiais

- `materials/starter/lifetime.c`: alvo original defeituoso, a corrigir.
- `materials/starter/variation.c`: ponto de partida incompleto para a CLI.
- `materials/checks/check.py`: verificação pública das correções sob ASan/LSan.
- `materials/experiments/observe.py`: execução controlada do alvo original.
- [Referências orientadas](references.md): ferramenta e leitura de código real.

## Etapas da investigação

1. **Prever.** Desenhe o bloco de 11 bytes, incluindo o terminador. Indique o
   proprietário e a visão antes e depois de `descarta`. Entregue o desenho antes
   de executar. Preveja se atribuir `NULL` a `m.texto` modifica `visao`.
2. **Observar.** Execute o experimento do guia dos materiais antes de editar.
   Guarde stderr, status e versão do compilador. Identifique no diagnóstico a
   allocation, a liberação e o acesso, com função e linha, sem fixar endereços.
3. **Explicar.** Relacione os três pontos do diagnóstico ao desenho. Explique por
   que o defeito independe de outra allocation reutilizar o endereço e por que uma
   impressão aparentemente correta sem ASan não valida o acesso.
4. **Corrigir.** Edite `lifetime.c`. Justifique a ordem das operações e a única
   liberação. Implemente a variação em arquivo separado, conforme o contrato.
5. **Verificar.** Execute os checks e registre os quatro offsets centrais.
   Revise o código para demonstrar que validação precede a formação da visão.
   Explique por que passar nos testes não prova ausência de todo comportamento
   indefinido e por que ASan não detecta apenas a formação de todo ponteiro inválido.

## Critérios de conclusão

- Relato identifica allocation, liberação e acesso inválido do original.
- `lifetime.c` mantém `Club\n`, status 0 e libera o bloco exatamente uma vez.
- Variação produz as três saídas e rejeita 11 antes de formar a visão.
- Checks passam com detecção de memory leaks ativa; revisão explica os invariantes
  de ownership, limites e caminho de falha de allocation.
- Patch e evidências distinguem o diagnóstico esperado inicial de uma falha de preparação.

## Extensões opcionais

Crie uma cópia independente que sobreviva ao descarte da mensagem original.
Documente quem libera cada bloco e trate falha de allocation. Em arquivos separados,
investigue buffer overflow, double-free ou leitura não inicializada. ASan não é
uma ferramenta geral para detectar dados não inicializados; selecione outra
ferramenta para esse caso. Comparações com Rust também são opcionais.

## Participação no clube

Compartilhe o patch, os comandos e um relato conforme o [modelo](report-template.md).
Inclua uma dúvida concreta e a explicação de um invariante. Remova caminhos pessoais
dos logs se necessário. Uma tentativa com diagnóstico bem explicado ajuda a discussão,
mesmo antes da correção. Proponha melhorias com um caso reproduzível.

## Referências e atividades relacionadas

Comece pela [documentação e leitura orientada](references.md). Depois relacione
esta investigação com alocadores: possuir um bloco exige saber quando liberá-lo.
O laboratório de compilação ajuda a entender a instrumentação do executável.
