# Contrato de scaled dot-product attention

O núcleo usa Python 3.10 ou posterior e biblioteca padrão. Implemente as operações
com aritmética explícita; não use NumPy, frameworks de deep learning ou autograd.
As três funções públicas ficam em `materials/attention.py`. Funções auxiliares
para produto matricial e transposição podem ficar nesse mesmo arquivo.

## Entradas e erros

Matrizes são `list` de linhas `list`, retangulares e não vazias. Os elementos
devem ser `int` ou `float` nativos, exceto `bool`, finitos, com módulo até
`1_000_000`. Tuplas, strings, complexos, NaN e infinitos são inválidos.
Converta os valores aceitos para a aritmética `float` do Python (binary64 no
ambiente de referência). Verifique os limites antes de construir intermediários.

| Entrada | Dimensão | Limite inclusivo |
| --- | --- | --- |
| Q, consultas | N × d_k | 1 ≤ N ≤ 256; 1 ≤ d_k ≤ 64 |
| K, chaves | N × d_k | Mesmo N e d_k de Q |
| V, valores | N × d_v | Mesmo N de Q; 1 ≤ d_v ≤ 64 |
| causal | `bool` | `True` ou `False`; não aceitar 0/1 |

Qualquer violação deve levantar `ValueError`, inclusive tipo incorreto.
Não se exige texto literal da exceção; informe a causa em uma mensagem clara.
Entradas devem permanecer intactas tanto no sucesso quanto na falha.
Cada chamada válida devolve listas novas; alterações no resultado não podem
alterar entradas nem resultados de chamadas anteriores. Não mantenha estado global.
Linhas e matrizes do resultado devem ser independentes entre si: alterar uma
linha não pode alterar outra por compartilhamento da mesma lista.

## Interfaces e resultados

`scaled_scores(q, k)` devolve `S = Q × Kᵀ / sqrt(d_k)`, uma lista N × N.
A posição `S[i][j]` compara a consulta i com a chave j. Implemente a transposição
e os produtos explicitamente. O limite do módulo de S é `8e12`; a faixa de
entrada evita overflow nos produtos e somas, mas não evita overflow de `exp(S)`.

`softmax(row)` recebe uma lista de 1 a 256 números nativos. Aceita finitos com
módulo até `1e15` e `float('-inf')`; rejeita `bool`, NaN, `+inf` e demais tipos.
Devolve uma lista de probabilidades da mesma extensão. Subtraia o maior valor
finito antes de exponenciar. Uma posição `-inf` deve produzir exatamente `0.0`.
Uma linha composta apenas de `-inf` deve levantar `ValueError`: não há distribuição
normalizada definida por este contrato. Underflow de contribuições muito pequenas
para zero é permitido. A soma da linha deve ficar a até `1e-12` de 1.

`attention(q, k, v, *, causal=False)` devolve um `dict` com exatamente:

- `scores`: S antes da causal mask, N × N;
- `probabilities`: P = softmax(S + M) por linha, N × N;
- `output`: O = P × V, N × d_v.

Com `causal=False`, M é zero. Com `causal=True`, M[i][j] é `-inf` quando
`j > i` e zero nos demais casos. A diagonal permanece permitida; assim,
attention nunca produz uma linha totalmente mascarada. Não há máscara arbitrária
na interface. Não aplique a causal mask depois da normalização e não altere `scores`.
A saída na posição i não pode depender de K ou V em posições posteriores a i.

Todos os resultados, exceto a causal mask interna, devem ser finitos. Os checks usam
`math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12)` para números;
formas, chaves do dict, exceções e zeros mascarados são conferidos exatamente.
Não arredonde intermediários para obter coincidência textual com os fixtures.

## Custo e escopo

Materialize S e P para observar o custo de duas matrizes N × N. O modelo de
armazenamento denso binary64 prevê `8*N*N` bytes por matriz, ou `16*N*N` pelas
duas, sem contar Q/K/V e saída. Listas Python têm referências, headers e
objetos numéricos: sua memória observada não é igual a essa previsão.
Meça a implementação após os checks; não confunda `tracemalloc` com RSS ou
memória GPU. Tiling, KV cache, projeções, treinamento e multi-head são extensões.

Na validação Python, compare o módulo antes de converter para `float`: `abs(x) > limite` funciona com `int` de qualquer tamanho; `float(x)` pode levantar `OverflowError` antes do `ValueError` exigido.
