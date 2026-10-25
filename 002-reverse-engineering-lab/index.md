---
title: Laboratório de Engenharia Reversa
area: compilation-execution
slug: 002-reverse-engineering-lab
summary: Reconstrua a decisão de um executável e justifique suas restrições com disassembly.
question: Como reconstruir uma decisão observando instruções de máquina?
draft: false
publishedAt: 2026-10-25
topics: [Engenharia reversa, Disassembly, Fluxo de controle]
prerequisites: [Funções em C, Arrays, Strings, Operadores bitwise, Hexadecimal]
tools: [GCC, GNU objdump, Python 3, GDB opcional]
environment: Linux x86-64
difficulty: intermediate
---

## O que vamos investigar

Um disassembly representa instruções de máquina em texto. Você investigará como
comparações e saltos decidem aceitar ou rejeitar uma entrada. O objetivo é
reconstruir e explicar essa decisão, ligando cada restrição a instruções concretas.

### Contrato técnico

O alvo original do Anexo A chama-se agora `gate.c`. Seu conteúdo, suas comparações
e suas mensagens permanecem iguais. `main` exige exatamente um argumento. Se a
quantidade divergir, escreve `uso: <argv[0]> CHAVE\n` em stderr, deixa stdout vazio
e retorna 2. Com um argumento, `confere` valida uma string de seis bytes; não são
seis caracteres Unicode. A entrada da CLI não pode conter byte NUL interno.

Se a validação rejeitar a entrada, stdout contém `porta fechada\n` e o status é 1.
Se aceitar, stdout contém `porta aberta\n` e o status é 0. Nesses dois casos,
stderr fica vazio. Os casos públicos iniciais são ausência de argumento, `ABC`
e `AAAAAA`. As restrições serão reconstruídas pelo participante.

O alvo está completo: não há funções a preencher. Alterar o executável para
aceitar qualquer entrada ou encontrar uma entrada sem explicar o disassembly
não satisfaz a atividade.

## Antes de começar

### Linguagens e ambiente

Referência: **C + x86-64**. Aceitas: C no alvo original; Rust somente para comparação.
Recomendadas: Rust para comparação. Linux x86-64; preservar gate.c e os alvos O0/O2.
Materiais oficiais: C + x86-64 existente.
Equivalência: apenas comparativa para outro alvo.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
A restrição preserva o mecanismo observado no núcleo.

Conheça funções, argumentos, strings e arrays em C, aritmética inteira e operadores
bitwise. Revise registradores, endereços e hexadecimal conforme necessário.
Use Linux x86-64, GCC, GNU objdump e Python 3. GDB é opcional.
O [guia local](materials/README.md) prepara ambos os alvos com comandos completos.

Guarde o fonte durante a primeira análise. Ele acompanha o pacote para permitir
compilação local; essa separação é uma disciplina da experiência, não um segredo
ou uma proteção técnica. Evite abrir o C ou usar disassembly com fonte intercalado
antes de registrar suas hipóteses.

## Materiais

- [Guia dos materiais](materials/README.md): preparação e contrato autocontidos.
- Fonte original em `materials/source-archive/gate.c`: reserve a leitura para o confronto final.
- [Preparação](materials/experiments/prepare.py): builds `-O0`/`-O2` e disassembly.
- [Checks públicos](materials/checks/check.py): status e canais da CLI sem chave aceita.
- [Guia local do laboratório](README.md) e [referências orientadas](references.md).
- [Modelo de relato](report-template.md): registro de hipóteses e evidências.

## Etapas da investigação

1. **Prever.** Registre o comportamento esperado para os três casos públicos.
   Desenhe como uma comparação pode conduzir à rejeição; não consulte o fonte.
2. **Observar.** Prepare os alvos, execute os checks e localize `main`, `confere`
   e a verificação de comprimento no disassembly `-O0`. Registre instruções e status.
3. **Explicar.** Reconstrua todas as restrições. Para cada uma, indique bytes lidos,
   operação, comparação, destino do salto e trecho de instruções que a sustenta.
   Distinga offset na string, endereço virtual e valor de byte.
4. **Implementar.** Construa seu modelo de decisão em pseudocódigo ou código próprio,
   sem modificar o alvo. Deduza uma entrada aceita e uma quase correta. Identifique
   a comparação específica que rejeita a segunda, considerando a ordem de avaliação.
5. **Verificar.** Execute as duas entradas, registre saída/status e confronte o modelo
   com o fonte guardado. Documente divergências entre previsão e observação.
   A chave sozinha não demonstra a reconstrução.

## Critérios de conclusão

Entregue relato com ambiente e comandos, tabela de todas as restrições ligada ao
disassembly, verificação de comprimento e interpretação dos status 2/1/0.
Demonstre uma entrada aceita e uma quase correta rejeitada, com a comparação
responsável e a sequência de execução que sustenta essa conclusão. Explique o
efeito da leitura como `unsigned char`, das promoções inteiras e do curto-circuito
das condições, usando evidência do executável e do confronto final com C.

Os checks públicos devem passar, mas não comprovam que alguma entrada é aceita.
Verifique sua entrada local com a opção documentada e registre o confronto final.
Não exija endereços ou registradores idênticos entre toolchains.

## Extensões opcionais

Compare `-O0` e `-O2` conforme o [experimento](materials/README.md#comparar-otimizações).
Localize a lógica equivalente mesmo se o símbolo `confere` desaparecer. Execute
as mesmas entradas nos dois alvos e explique transformações observadas sem assumir
que a otimização reproduz a estrutura do C. Com GDB, observe uma comparação e
um salto com `break confere`, `run AAAAAA`, `disassemble confere` e `nexti` no alvo `-O0`.

## Participação no clube

Compartilhe hipótese, trecho de disassembly, comando e resultado. Ao pedir ajuda,
mostre a primeira relação entre instruções e predicado que ficou incerta. Preserve
a descoberta dos colegas: evite divulgar a chave ou a tabela resolvida na discussão
inicial. Sugestões de checks devem identificar o requisito que verificam.

## Referências e atividades relacionadas

As [referências](references.md) orientam a leitura de objdump, otimizações e código
real do Capstone. O laboratório complementa representação binária e compilação.
O Bomb Lab de CS:APP é inspiração metodológica; este alvo pertence ao caderno do
Oxide Club e não reproduz seus desafios.
