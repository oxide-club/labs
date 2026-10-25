# Origem dos casos conhecidos

Os dados em [cases.json](cases.json) são autorais, sob CC0-1.0. Não foram obtidos
executando o starter nem uma implementação geral de attention. Os scores foram
calculados à mão; probabilidades e saídas abaixo são expressões escalares fechadas.
`checks/verify_fixtures.py` usa Decimal com 60 dígitos para conferir essas expressões.

No caso `scaled-asymmetric`, d_k=4 e o divisor é 2. A primeira consulta produz
produtos `[2,0]`; a segunda produz `[2,8]`. Os scores são `[[1,0],[1,4]]`.
Defina `p = 1/(1+exp(-1))` e `r = 1/(1+exp(3))`. As probabilidades são
`[[p,1-p],[r,1-r]]`. Para cada primeira probabilidade x, a saída é
`[4*x-2, 4*x, 3-2*x]`. Essas identidades permitem conferir as saídas sem
reimplementar os produtos matriciais nos checks de referência.

No caso `scaled-causal`, a primeira linha recebe pesos `[1,0]`, portanto a
primeira saída coincide com V[0]. A segunda linha e os scores brutos permanecem
iguais aos do caso sem causal mask. Uma implementação que modifica os scores ao
mascarar falha na comparação dos intermediários.

No caso `uniform-three-positions`, todas as consultas são zero. Cada score é
zero e cada probabilidade vale 1/3; a média das três linhas de V é `[-1,1]`.
No caso `single-negative-score`, há apenas uma posição: score -6, probabilidade
1 e saída igual a `[-7,4]`. O sinal negativo do score não altera esse peso único.

O quinto caso, `irrational-scale`, usa d_k=2 e produtos diagonais 1 e 2.
Os scores são `[[1/sqrt(2),0],[0,sqrt(2)]]`. Defina
`a = 1/(1+exp(-1/sqrt(2)))` e `b = 1/(1+exp(sqrt(2)))`; as probabilidades
são `[[a,1-a],[b,1-b]]`. V é a matriz identidade 2 × 2, portanto a saída
coincide com as probabilidades. A conferência usa `Decimal(2).sqrt()` e
exponenciais escalares com 60 dígitos, sem implementar attention geral.

Esse caso distingue a escala correta de `int(sqrt(d_k))`: truncar sqrt(2)
para 1 produziria scores `[[1,0],[0,2]]`. O segundo teste de
`checks/verify_fixtures.py` verifica que os scores, as probabilidades e a saída
desse vetor incorreto são rejeitados, cada campo separadamente, pelas mesmas
tolerâncias do check público. Os quatro primeiros casos não cobriam essa falha.

O JSON guarda aproximações decimais de binary64, não promessas de igualdade
bit a bit. A tolerância está no [contrato](../contract.md). Os checks também
usam casos de softmax com scores grandes; não exija que exp(1000) seja representável.
