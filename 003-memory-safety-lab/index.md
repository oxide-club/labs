---
title: Laboratório de Segurança de Memória
area: memory
slug: 003-memory-safety-lab
summary: Diagnostique um use-after-free e corrija o lifetime sem causar memory leak.
question: Quando um pointer deixa de permitir acesso aos dados?
draft: false
publishedAt: 2026-10-25
topics: [Memória, C, Lifetime]
prerequisites: [malloc e free, Pointers e strings, Leitura de stack traces]
tools: [Compilador C11, AddressSanitizer, Python 3]
environment: Linux x86-64 com GCC ou Clang e runtime AddressSanitizer
difficulty: intermediate
---

## O que vamos investigar

### O que você vai corrigir e construir

Você tem **duas tarefas obrigatórias**: corrigir um acesso à memória após dealocação
e implementar uma variação que aceita um offset pela linha de comando.

| Arquivo em `materials/starter/` | Seu trabalho |
| --- | --- |
| `lifetime.c` | Observar o erro com ASan e corrigir a ordem das operações, mantendo a saída `Club`. |
| `variation.c` | Validar o offset e imprimir o trecho da mensagem que começa nessa posição. |

A alocação da mensagem contém dez caracteres e um terminador zero:

```text
posição: 0 1 2 3 4 5 6 7 8 9 10
byte:    O x i d e   C l u b \0
                     ↑
              view no offset 6
```

A view aponta para dentro do mesmo bloco; ela não é uma cópia da mensagem.
Ao fazer dealocação do bloco, perde-se também a possibilidade de ler essa view.
Na variação, o offset 6 imprime `Club`, 10 imprime uma linha vazia e 11
precisa ser rejeitado antes de formar a view.

Entregue as duas implementações e um relato que ligue o diagnóstico original
à correção: onde o bloco nasce, quando é lido e quem faz sua dealocação exatamente uma vez.

### Conceitos para a investigação

Guardar o endereço de um objeto em um pointer não prolonga seu lifetime, isto é, o intervalo em que ele existe segundo o modelo da linguagem.
Um *use-after-free* ocorre quando o programa acessa um bloco depois de fazer sua dealocação.
Você vai usar o AddressSanitizer (ASan) para relacionar a alocação, a dealocação e
o acesso inválido. Depois, vai corrigir a causa sem introduzir um memory leak.

#### Contrato técnico

O arquivo `materials/starter/lifetime.c` contém o programa original `vida.c`.
Ele faz alocação de `"Oxide Club"` e cria uma view a partir do offset 6, ou
seja, um pointer para uma posição dentro do mesmo bloco. Em seguida,
faz dealocação da mensagem e tenta ler a view. O defeito inicial é intencional.
Corrija esse arquivo mantendo `Club\n` em stdout, status 0 e uma única dealocação
do bloco. Se `malloc` falhar, preserve o status 2. Todos os acessos devem ocorrer
durante o lifetime do bloco. Não remova a alocação nem substitua a mensagem por
uma string estática para contornar a investigação.

Depois, implemente `materials/starter/variation.c`. Sua interface de linha de
comando (CLI) é `variation DESLOCAMENTO`.
Aceite exatamente um argumento não vazio com dígitos ASCII de `0` a `9`, sem
sinal nem espaços, cujo valor esteja entre 0 e 10. Zeros à esquerda são aceitos.
Rejeite valores maiores sem overflow na conversão. Valide antes de formar a
view, inclusive antes de formar o pointer no offset 11. Embora seja
possível formar um pointer one-past para este bloco de 11 bytes, ele não é uma
view de string válida; o contrato exige a rejeição antes dessa formação.

| Entrada | stdout exata | Status |
| --- | --- | ---: |
| `0` | `Oxide Club\n` | 0 |
| `6` | `Club\n` | 0 |
| `10` | `\n` | 0 |
| `11`, argumento inválido ou quantidade incorreta | vazia | 2 |

Em sucesso, stderr fica vazia. Em erro de argumento, stderr deve conter exatamente
`Erro: use um deslocamento decimal entre 0 e 10.\n`. Em falha de alocação, retorne
2, não escreva em stdout e faça a limpeza de qualquer recurso já adquirido; a mensagem em
stderr não é fixada. Mantenha alocação dinâmica, cópia dos 11 bytes e uma única
dealocação em cada execução bem-sucedida. A view faz borrowing do acesso ao bloco: ela não é uma segunda
alocação e não deve ser passada a `free`. Os checks não simulam falta de memória;
explique esse caminho na revisão do código.

## Antes de começar

### Linguagens e ambiente

A parte obrigatória usa **C11 e AddressSanitizer** para observar a alocação, a dealocação e o
acesso inválido. Os materiais fornecem código em C11.

C++ e Rust são recomendados para comparações. Essas comparações complementam a
investigação do defeito em C, mas não a substituem.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Conheça `malloc`, `free`, arrays, strings terminadas em zero e aritmética de
pointers. Instale Python 3 e GCC ou Clang com runtime ASan. Linux x86-64 é o
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
   owner e a view antes e depois de `descarta`. Entregue o desenho antes
   de executar. Preveja se atribuir `NULL` a `m.texto` modifica `visao`.
2. **Observar.** Execute o experimento do guia dos materiais antes de editar.
   Guarde stderr, status e versão do compilador. Identifique no diagnóstico a
   alocação, a dealocação e o acesso, com função e linha, sem fixar endereços.
3. **Explicar.** Relacione os três pontos do diagnóstico ao desenho. Explique por
   que o defeito independe de outra alocação reutilizar o endereço e por que uma
   impressão aparentemente correta sem ASan não valida o acesso.
4. **Corrigir.** Edite `lifetime.c`. Justifique a ordem das operações e a única
   dealocação. Implemente a variação em arquivo separado, conforme o contrato.
5. **Verificar.** Execute os checks e registre os quatro offsets centrais.
   Revise o código para demonstrar que validação precede a formação da view.
   Explique por que passar nos testes não prova ausência de todo undefined behavior e por que ASan não detecta apenas a formação de todo pointer inválido.

## Critérios de conclusão

- Relato identifica alocação, dealocação e acesso inválido do original.
- `lifetime.c` mantém `Club\n`, status 0 e faz dealocação do bloco exatamente uma vez.
- Variação produz as três saídas e rejeita 11 antes de formar a view.
- Checks passam com detecção de memory leaks ativa; revisão explica os invariantes
  de ownership, limites e caminho de falha de alocação.
- Patch e evidências distinguem o diagnóstico esperado inicial de uma falha de preparação.

## Extensões opcionais

Crie uma cópia independente que sobreviva ao descarte da mensagem original.
Documente quem faz dealocação de cada bloco e trate falha de alocação. Em arquivos separados,
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
esta investigação com allocators: possuir um bloco exige saber quando fazer sua dealocação.
O laboratório de compilação ajuda a entender a instrumentação do executável.
