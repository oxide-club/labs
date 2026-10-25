---
title: Laboratório de Representação Binária
area: data-protocols
slug: 001-binary-lab
summary: Investigue como valor numérico, layout em memória e formato externo se relacionam.
question: Quando os mesmos valores produzem bytes diferentes, e quais bytes permitem perceber a diferença?
draft: false
publishedAt: 2026-10-25
updatedAt: 2026-10-25
topics: [Representação binária, Endianness, Layout, Serialização]
prerequisites: [Funções em C, Arrays, Unsigned integers, Hexadecimal]
tools: [GCC ou Clang, Python 3]
environment: C11 com bytes de oito bits e tipos uint8_t uint16_t e uint32_t
difficulty: intermediate
relatedChallenges: [005-base64, 013-record-inspector]
---

## O que vamos investigar

Um inteiro, seus bytes na memória e os bytes de um arquivo são coisas relacionadas,
mas diferentes. Você vai investigar **quais observações distinguem essas representações**.
O instrumento já está completo. O trabalho central é formular hipóteses, escolher
entradas que as discriminem, observar e explicar.

A investigação tem duas comparações controladas:

- Preserve o valor de uma word de 32 bits e altere a ordem externa entre LE e BE.
- Preserve os valores de três campos e altere sua ordem de declaração em duas structs C.

Little-endian (LE) escreve primeiro o byte menos significativo; big-endian (BE)
escreve primeiro o mais significativo. Essa regra define um formato externo.
Ela não determina automaticamente o layout que seu compilador usa para uma struct.

Uma hipótese como “o host usa LE” precisa de uma entrada capaz de distingui-la de BE.
`0xFFFFFFFF` não permite essa distinção. Investigue por quê e escolha um contraexemplo.
Não é necessário ter acesso a uma segunda arquitetura: as duas codificações externas
são produzidas explicitamente no mesmo host. Essa comparação não emula outra CPU.

### Instrumento e limites

[representation.c](materials/experiments/representation.c) produz três codificações:
bytes do host, bytes externos LE e bytes externos BE. Também lê bytes LE como BE
para expor uma interpretação incompatível. Em seguida, observa tamanho, alignment
e offsets de duas structs, sem ler ou comparar seus bytes de padding.

As structs contêm `tag` de 8 bits, `length` de 32 e `flags` de 16. A ordem dos membros
muda, mas seus valores são iguais. O formato externo de sete bytes mantém a ordem
`tag`, `length` LE32 e `flags` LE16. Ele não é o header compactado da extensão histórica.

## Antes de começar

### Linguagens e ambiente

Use C11 para observar o layout dos objetos C fornecidos. Você pode usar Python,
Rust, Go ou outra linguagem para analisar os logs e implementar a extensão de
serialização. Uma estrutura de outra linguagem é uma comparação adicional, não
uma observação do layout C. Não há dependências externas.

Conheça hexadecimal, shifts e arrays. Registre sistema, arquitetura, compilador e
flags. Siga os comandos do [guia de materiais](materials/README.md).
Não use cast de um array de bytes para pointer de inteiro para interpretar os dados.
O instrumento usa acesso por `unsigned char` à word e conversões explícitas.

## Materiais

- [Instrumento completo](materials/experiments/representation.c).
- [Guia de execução e registro](materials/README.md).
- [Modelo de relato](report-template.md) para hipóteses, evidências e limitações.
- [Contrato histórico opcional](materials/legacy.md), com starter, vetores e checks do header.

Os checks do header antigo verificam aquela implementação opcional. Eles não avaliam
esta investigação e não precisam passar para iniciá-la ou concluí-la.

## Etapas da investigação

### 1. Formular hipóteses discriminantes

Antes de executar, registre duas interpretações possíveis para os bytes do host:
LE e BE. Preveja os bytes de `0x01020304`, `0x22500102` e `0xFFFFFFFF` em ambas.
Identifique qual entrada não distingue as hipóteses. Admita outra ordem se os dados
não sustentarem nenhuma delas, em vez de forçar uma classificação.

Formule também uma hipótese sobre as structs: mesmos campos e valores implicam
mesmo tamanho, mesmos offsets e mesma representação externa? Separe essas três afirmações.
Desenhe uma tabela prevista, marcando o que depende da ABI e precisa ser observado.

### 2. Observar bytes e interpretações

Compile o instrumento e salve a saída original. Para cada word, compare host, LE e BE.
Relacione a coluna `wrong` à leitura de bytes LE por um leitor BE.
Explique por que o valor numérico não muda ao escolher outra codificação, mas muda
quando os mesmos bytes recebem uma interpretação incompatível.

Escolha uma quarta word que discrimine LE de BE e acrescente-a ao array `words` numa
cópia do instrumento. Preveja o resultado antes de executar. Essa pequena alteração
é a implementação obrigatória; entregue o patch e a observação correspondente.

### 3. Investigar o layout

Registre `sizeof`, `_Alignof` e `offsetof` de A e B. Calcule os intervalos ocupados
pelos campos, os intervalos de padding e o espaço após o último campo.
Não suponha um tamanho universal nem uma diferença obrigatória entre os tamanhos.
Mesmo se os tamanhos coincidirem, verifique separadamente os offsets.

Confronte a hipótese com `logical_equal` e `external_equal`. Explique por que igualdade
de campos e de bytes serializados não exige igualdade de layout.
Acrescente a uma cópia do instrumento um campo `uint8_t marker` no início de A,
sem mudar o formato externo. Preveja quais offsets podem mudar, meça e explique.
Mantenha o marker fora da igualdade dos três campos originais.

### 4. Confrontar uma hipótese de round-trip

Usando as funções do instrumento, acrescente numa cópia uma leitura LE explícita.
Demonstre uma ida e volta BE→leitura BE que recupera a word, embora um consumidor
que exija LE interprete aqueles bytes incorretamente. Use uma word discriminante.
Compare com bytes LE calculados independentemente. Explique qual teste distingue
“o par desfaz suas próprias operações” de “o par implementa o formato combinado”.

### 5. Explicar o alcance das evidências

Repita as observações com `-O0` e `-O2`. Não é obrigatório observar diferenças.
Separe propriedades do formato, observações desta ABI e conclusões não demonstradas.
Escolha uma hipótese que os dados rejeitam ou delimitam. Se sua previsão estava
correta, apresente uma hipótese alternativa rejeitada; não invente um erro inicial.

## Critérios de conclusão

Entregue o relato, os comandos, os logs e suas alterações instrumentais. O relato deve conter:

- Hipóteses anteriores à execução, incluindo um caso que não as distingue.
- Tabela de bytes para as quatro words e explicação da interpretação incompatível.
- Tamanhos, offsets e padding de A/B, antes e depois de adicionar o marker.
- Evidência de que igualdade lógica e formato externo podem sobreviver à mudança de layout.
- Contraexemplo no qual round-trip passa e o formato externo está errado.
- Comparação O0/O2, ambiente e limites de generalização.

O programa funcional, sozinho, não conclui o laboratório. Outra pessoa deve conseguir
reproduzir as observações e entender qual hipótese cada comparação sustenta ou rejeita.
Não use igualdade de memória bruta de structs como prova de igualdade dos campos.

## Extensões opcionais

Implemente o header compactado de quatro bytes do [guia histórico](materials/legacy.md).
Se fizer essa extensão, preserve sua API e rode seus checks e UBSan.
Você também pode comparar outra arquitetura ou outra ABI, registrando o ambiente.
Essas atividades não substituem as comparações obrigatórias.

## Participação no clube

Compartilhe uma hipótese, o caso que a distingue de uma alternativa e os bytes observados.
Ao pedir ajuda, inclua comando, compilador e a primeira diferença que não conseguiu explicar.
Use o [modelo de relato](report-template.md); preserve previsões anteriores à coleta.

## Referências e atividades relacionadas

As [referências orientadas](references.md) apoiam a explicação de tipos, shifts e formatos externos.
Base64 e o inspetor de registros são desafios de implementação relacionados.
Este laboratório investiga por que uma representação funciona e o que suas observações permitem concluir.
