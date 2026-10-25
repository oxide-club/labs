---
title: Laboratório de Cache e Locality
area: memory
slug: 005-cache-lab
summary: Construa um simulador de cache. Compare sequências de acesso à memória. Explique os resultados com tabelas e arquivos de entrada.
question: Como a sequência de endereços muda os hits de uma cache?
draft: false
publishedAt: 2026-10-21
updatedAt: 2026-10-25
topics: [Cache, Locality, Direct mapping]
prerequisites: [Operadores bitwise, Structs em C, Leitura de arquivos]
tools: [GCC ou Clang, Python 3]
environment: C11 com uint64_t e terminal Linux
difficulty: intermediate
---

## O que vamos investigar

### O que você vai construir

Você vai entregar **dois programas e uma análise**: um simulador de cache e um
gerador de acessos a uma matriz. O simulador recebe endereços de um arquivo de
texto e conta hits, misses e evictions. O gerador permite comparar a
leitura da mesma matriz por linhas e por colunas.

```text
gerador da matriz → arquivo de acessos → simulador → contadores
traces fornecidos ──────────────────────↗
```

Como exemplo pequeno, comece com uma cache vazia e leia `0x00` e depois `0x01`.
A primeira leitura causa um miss e carrega o bloco de 16 bytes; a segunda é um
hit, porque pertence ao mesmo bloco. O resultado é
`hits=1 misses=1 evictions=0`.

Implemente o simulador em `materials/starter/cache.c` ou na linguagem escolhida.
Depois crie o gerador e produza quatro traces: linhas e colunas para `N=8` e
`N=16`. Entregue ambos os códigos, os traces e um relato explicando os contadores.
Os endereços são números do modelo; o experimento não mede a cache real da CPU.

### Conceitos para a investigação

Você vai construir um simulador para investigar como a sequência de endereços
afeta os hits de uma cache. Depois, vai comparar dois percursos da mesma matriz.
A entrega inclui o código, os resultados dos experimentos e uma explicação.

#### Termos usados neste laboratório

- **Bloco:** grupo de 16 bytes consecutivos. O primeiro endereço de cada bloco é um múltiplo de 16.
- **Cache line:** posição que guarda um bloco.
- **Direct mapping:** cada bloco só pode ocupar uma cache line específica.
- **Tag:** valor que identifica qual bloco ocupa uma cache line.
- **Hit:** acesso a um bloco que já está na cache.
- **Miss:** acesso a um bloco que não está na cache.
- **Eviction:** retirada do bloco atual de uma cache line válida para dar lugar a outro.
- **Trace:** arquivo que registra uma sequência de acessos.
- **Locality:** uso repetido dos mesmos endereços ou de endereços próximos.

#### Modelo da cache

A cache tem **quatro cache lines de 16 bytes**, com direct mapping.
A capacidade total é de 64 bytes de dados.
Cada cache line guarda uma tag e um indicador de validade.
No início de cada execução, todas as cache lines estão inválidas e todos os contadores estão em zero.

Cada linha do trace tem o formato `L 0xENDERECO`.
Ela representa a leitura de um byte.
O endereço é um unsigned integer de 64 bits, com até 16 dígitos hexadecimais.
Os traces fornecidos contêm apenas entradas válidas.
Os endereços pertencem ao modelo. **Não converta esses endereços em pointers.**

Para um endereço `a`, calcule:

- `offset = a & 0xF`: posição do byte dentro do bloco;
- `index = (a >> 4) & 0x3`: índice da cache line;
- `tag = a >> 6`: identificação do bloco nessa cache line.

Se a cache line estiver válida e sua tag for igual à tag calculada, conte um hit.
Caso contrário, conte um miss.
Em um miss, grave a nova tag e marque a cache line como válida. Se ela já estava
válida antes desse acesso, conte também uma eviction.

No modelo, um miss carrega o bloco inteiro.
O simulador não precisa guardar os bytes desse bloco.
Cada acesso lê apenas um byte. Portanto, nenhum acesso atravessa dois blocos.

Ao terminar, escreva uma linha no formato `hits=N misses=N evictions=N`.
Em uma execução bem-sucedida, retorne o código de saída zero.
Os contadores devem sempre atender a estas condições:

- `hits + misses == leituras`;
- `evictions <= misses`.

Uma tag com valor zero não indica que a cache line está válida.
Use o indicador de validade para verificar essa condição.

## Antes de começar

### Linguagens e ambiente

A implementação de referência usa **C11**, mas você pode escolher outra linguagem,
como C, Rust, Go ou Python. Rust, Go e Python são alternativas recomendadas.
Preserve o modelo: endereços sintéticos de 64 bits, quatro cache lines de 16 bytes e
direct mapping.

Há código inicial em C11 e em Rust (`materials/starter/rust/`). Implementações em
outras linguagens podem cumprir o mesmo contrato da parte obrigatória.

Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).

Você precisa conhecer operadores bitwise, structs e leitura de arquivos em C.
Use GCC ou Clang com suporte a C11 e ao tipo `uint64_t`.
Use Python 3 para executar as verificações públicas.
As instruções usam um terminal Linux.

1. Baixe o pacote de materiais.
2. Extraia o pacote.
3. Abra um terminal no diretório do laboratório extraído.
4. Execute os comandos abaixo.

```sh
cc --version
python3 --version
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/starter/cache.c -o cache
```

O código inicial compila, mas ainda não simula a cache.
Registre no relato as versões das ferramentas e as opções de compilação.
Depois de implementar o simulador, execute `./cache < materials/inputs/trace-a.txt`.

## Materiais

- [Guia dos materiais](materials/README.md): descrição dos arquivos e comandos de uso.
- [Código inicial em C](materials/starter/cache.c): arquivo para implementar o simulador.
- [Trace A](materials/inputs/trace-a.txt): oito acessos para prever os resultados à mão.
- [Trace B](materials/inputs/trace-b.txt): dezesseis acessos para verificar evictions.
- [Verificações públicas](checks/check.py): testes com resultados conhecidos e casos de limite.
- [Modelo de relato](report-template.md): instruções para registrar sua investigação.

Você também deve criar o gerador de percursos da matriz.
Antes de consultar os resultados de conferência, registre sua previsão.

## Etapas da investigação

### 1. Prever os acessos

1. Leia o trace A antes de implementar o simulador.
2. Preencha uma tabela com os campos abaixo.
3. Explique quais acessos podem usar um bloco carregado por uma leitura anterior.

```text
Endereço | Offset | Índice | Tag | Válida antes? | Hit/miss | Eviction?
```

Guarde a tabela original, mesmo que sua previsão esteja errada.
Você vai comparar essa previsão com os resultados do simulador.

### 2. Implementar, observar e verificar

1. Implemente o simulador em `materials/starter/cache.c` ou em um arquivo seu.
2. Preserve os 64 bits de cada endereço durante a leitura.
3. Compile o simulador.
4. Execute o trace A em um novo processo.
5. Execute o trace B em outro processo.
6. Registre a saída e o código de saída de cada execução.
7. Execute as verificações públicas.

Os comandos abaixo usam `materials/starter/cache.c` como arquivo da implementação.

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/starter/cache.c -o cache
./cache < materials/inputs/trace-a.txt
./cache < materials/inputs/trace-b.txt
python3 checks/check.py ./cache
```

<details>
<summary>Conferir resultados dos traces</summary>

| Trace | Hits | Misses | Evictions |
| --- | ---: | ---: | ---: |
| A | 3 | 5 | 3 |
| B | 4 | 12 | 8 |

No trace A, os acessos `0x0F`, `0x4F` e `0x1F` são hits.
Os acessos `0x40`, `0x00` (segunda ocorrência) e `0x50` causam evictions em cache lines válidas.

</details>

Compare os resultados com sua previsão.
Se houver uma diferença, explique a causa.
Se você corrigir o simulador, registre a correção.
Depois, execute novamente as verificações públicas.

Verifique também estes casos:

- entrada vazia;
- uma leitura;
- duas leituras do mesmo endereço;
- endereços próximos do maior unsigned integer de 64 bits.

### 3. Investigar a locality

Esta etapa é obrigatória para concluir o laboratório.
A matriz `A[N][N]` contém bytes e ocupa endereços consecutivos, em row-major order.
O endereço inicial da matriz no modelo é zero.

Crie um gerador que escreva as leituras da matriz no formato de trace.
O gerador deve produzir dois percursos:

- **Por linhas:** para cada `i`, percorra `j`. Escreva o endereço `N*i+j`.
- **Por colunas:** para cada `j`, percorra `i`. Escreva o endereço `N*i+j`.

Em ambos os percursos, os índices variam de zero até `N-1`.
Use a linguagem de sua preferência para o gerador.
Documente o comando que executa o gerador.

1. Antes de executar, preveja qual percurso terá mais hits para `N=16`.
2. Faça outra previsão para `N=8`.
3. Gere os quatro traces: dois percursos para cada tamanho de matriz.
4. Confira se cada trace tem exatamente `N*N` leituras.
5. Execute cada trace em um novo processo do simulador.
6. Guarde os comandos, os traces e os contadores obtidos.

<details>
<summary>Conferir resultados de locality</summary>

| N | Percurso | Hits | Misses | Evictions |
| ---: | --- | ---: | ---: | ---: |
| 16 | Linhas | 240 | 16 | 12 |
| 16 | Colunas | 0 | 256 | 252 |
| 8 | Linhas | 60 | 4 | 0 |
| 8 | Colunas | 60 | 4 | 0 |

</details>

Explique por que os percursos têm os mesmos contadores quando toda a matriz cabe na cache.
Escolha dois endereços de blocos diferentes que usam a mesma cache line.
Mostre os índices e as tags desses endereços.

### 4. Explicar os resultados

Explique como a validade, a tag, a capacidade e a ordem de acesso afetam os resultados.
Explique por que blocos diferentes podem disputar a mesma cache line, mesmo que a cache tenha outras cache lines livres.
Inclua no relato a previsão original, uma tabela com os resultados conferidos
e os resultados das verificações da implementação.

## Critérios de conclusão

O laboratório está concluído quando a entrega atende a todos estes critérios:

- O simulador segue o modelo descrito e produz os resultados esperados para os traces A e B.
- O simulador passa nas verificações dos casos de limite.
- Cada execução começa com cache lines inválidas e contadores em zero.
- Os contadores atendem às duas condições descritas no modelo.
- A entrega inclui o gerador e os quatro traces da matriz.
- O relato contém a previsão, os comandos, o ambiente e os resultados observados.
- A explicação relaciona os resultados à locality e à disputa por cache lines.
- A explicação distingue a simulação de uma medição de CPU real.
- Suas instruções permitem que outra pessoa compile o código e repita os experimentos.

Entregue o código do simulador, o gerador, os traces e o relato.
As verificações públicas avaliam o programa. O relato deve explicar os resultados.
As extensões abaixo são opcionais.

## Extensões opcionais

Amplie o modelo para usar `S` sets, `E` ways por set e blocos de `B` bytes.
Uma way é uma posição para um bloco dentro de um set.

1. Verifique se `S` e `B` são potências de dois.
2. Verifique se `E` é positivo.
3. Verifique os tamanhos e os limites antes de fazer alocação de memória.

Use estas fórmulas:

- `bloco=a/B`;
- `set=(a/B)%S`;
- `tag=(a/B)/S`.

Implemente a política LRU: faça eviction do bloco usado há mais tempo.
Atualize o registro de uso em cada acesso.
Em um miss, escolha uma way inválida, se houver.
Se todas as ways estiverem válidas, faça eviction do bloco usado há mais tempo.
Em caso de empate, escolha a way com o menor número.

Com `S=1`, `E=2` e `B=16`, execute o trace `0x00, 0x10, 0x00, 0x20, 0x10`.
O resultado esperado é `hits=1 misses=4 evictions=2`.
Registre as alterações desta extensão separadamente das etapas obrigatórias.

## Participação no clube

Compartilhe sua previsão e o que você observou.
Você pode compartilhar uma tentativa incompleta.

Se tiver uma dúvida, inclua o menor trace que mostra o problema.
Inclua também o comando, a saída e sua pergunta.
Consulte [como participar](/como-participar/) para acessar a conversa do clube.

Para propor uma melhoria, siga o [guia de contribuição](https://github.com/oxide-club/labs/blob/main/CONTRIBUTING.md).
Use o mesmo guia para compartilhar uma solução com evidências.
Mantenha sua solução separada do código inicial.
Avise quando sua mensagem mostrar resultados que outras pessoas ainda precisam prever.

## Referências e atividades relacionadas

Consulte [as referências orientadas](references.md) para leituras e investigação de código real após concluir as etapas obrigatórias.

- [CS:APP — Lab Assignments](https://csapp.cs.cmu.edu/3e/labs.html): laboratórios que inspiraram os temas do clube.
- [CS:APP — Cache Lab](https://csapp.cs.cmu.edu/3e/cachelab.pdf): outro laboratório sobre cache.
- [Biblioteca do clube](/biblioteca): materiais para estudar os conceitos usados aqui.
- [Catálogo de desafios](/desafios/): atividades com objetivos definidos.
