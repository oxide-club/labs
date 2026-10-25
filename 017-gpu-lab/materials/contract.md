# Contrato executável

## Dados e limites

`long long` deve ter 64 bits. O ambiente de referência é Linux, C11 e CUDA C++14.
O CLI CPU recebe `n seed [mode]`; o CLI GPU recebe `n block seed [mode]`.
Sem `mode`, ambos usam o gerador periódico abaixo; os datasets de medição continuam iguais.
O modo opcional de fixture aceita `positive`, `negative` ou `ramp`. Os modos `positive` e `negative` preenchem tanto `a` quanto `b` com +1024 ou -1024, respectivamente; `seed` ainda deve estar na faixa, mas não altera os valores.
Com `n=MAX_N`, a reduction deve produzir +4294968320 ou -4294968320 e cada posição vetorial deve produzir +2048 ou -2048.
O modo `ramp` preenche `a[i]=b[i]=1024-(i mod 7)`; em `n=MAX_N`, sua soma é 4282385411, discriminando acumulação em float32. Os checks GPU exercitam os dois extremos e a rampa em todos os blocos aceitos. Modo desconhecido produz status 2 antes de operações CUDA.
Aceite números decimais: `0 <= n <= 4194305`, `0 <= seed <= 1000` e `block` em `{64,128,256,512}`.
Argumentos ausentes, não numéricos ou fora da faixa produzem status 2 sem operações CUDA.
Erro de memória, CUDA ou divergência produz status 1 e diagnóstico em stderr. Sucesso produz status 0.
Não há garantia sobre saídas parciais após um erro; não use tempos de uma execução que falhou.

O gerador define, para `0 <= i < n`:

```text
a[i] = ((17*i + seed) mod 2049) - 1024
b[i] = ((31*i + 3*seed) mod 2049) - 1024
```

A API aceita também outros vetores cujos valores estejam em `[-1024,1024]`.
O caller deve respeitar essa pré-condição; as funções device não precisam validar valores.
O valor máximo absoluto de qualquer soma parcial de `a` é `4194305*1024 = 4294968320`, muito abaixo de `LLONG_MAX`.
A soma vetorial pertence a `[-2048,2048]`. Use aritmética assinada de 64 bits em todas as passagens; não acumule em `int`.
A comparação é exata. Overflow está excluído pelos limites, não definido como wraparound.

## Interface GPU

```c
cudaError_t launch_add(const long long *a, const long long *b,
                       long long *out, size_t n, unsigned block);
cudaError_t launch_reduce(const long long *a, long long *out,
                          size_t n, unsigned block);
```

Os ponteiros são device pointers, com allocations distintas. `a` e `b` oferecem `n` valores, `out` da soma oferece `n`, e `out` da reduction oferece um valor.
Mesmo com `n=0`, o runner fornece buffers válidos. A soma vazia não escreve elementos; a reduction vazia deve escrever zero.
As funções devem usar somente o stream padrão, preservar entradas e retornar o primeiro erro de API/kernel launch encontrado.
O caller verifica erros assíncronos com `cudaDeviceSynchronize`; retorno de kernel launch não confirma conclusão.
Cada kernel launch interno deve verificar `cudaGetLastError`. Verifique também allocation, cópia e deallocation de buffers temporários.
Se houver falha, libere scratch próprio; o caller mantém ownership dos seus buffers.

A soma deve mapear threads a índices sem acessar `i >= n`.
A reduction deve ocorrer na GPU em uma ou mais passagens e produzir a soma de `a`.
Não copie valores parciais para somar na CPU. Não use CUB, Thrust ou outra reduction pronta.
Use memória compartilhada e sincronização explícita entre threads de um bloco em pelo menos a variante inicial.
Explique por que nenhuma thread deixa de alcançar uma barrier coletiva necessária.
Um bloco parcial deve contribuir com a identidade zero nas posições sem dado.
Não assuma sincronização entre blocos dentro de um kernel comum: use passagens distintas quando necessário.

## Verificação e medição

O runner compara cada posição de `a+b` e a soma com loops CPU independentes dos kernels.
Os checks CPU comparam esses loops com inteiros Python. Eles cobrem zero, fronteiras e tails para todos os blocos aceitos.
Testes não substituem a explicação dos invariantes ou uma ferramenta de detecção de acessos inválidos.
Recomenda-se executar `compute-sanitizer materials/build/gpu 513 256 9` após implementar.

Antes de cada execução, inclusive a medida, o runner preenche as saídas com bytes `0x7f`.
O valor inteiro resultante fica fora das duas faixas de saída válidas. O runner sincroniza essa preparação antes de iniciar os relógios.
Assim, a validação exige novas escritas e não aceita resultados residuais do aquecimento.
O caminho de sucesso libera explicitamente todos os buffers e eventos com verificação de retorno; os destruidores sem exceção são apenas fallback em caso de falha.

O runner faz uma execução sem temporização publicada para validar e aquecer. Só depois faz a amostra medida, também validada.
`kernel_ms` usa eventos CUDA no stream padrão ao redor das duas funções, incluindo todas as passagens da reduction.
O intervalo pode incluir esperas e overhead introduzidos dentro dessas funções; não representa apenas instruções aritméticas.
`h2d_ms` mede as duas cópias de entrada com relógio monotônico do host.
`d2h_ms` mede a cópia do vetor e do escalar de saída pelo mesmo relógio.
As cópias usam memória host paginável e API síncrona; os tempos incluem overhead da API e staging, não são banda pura do barramento.
`total_ms` vai do início da primeira cópia até o retorno da última cópia, incluindo kernel launches e sincronização.
Contexto CUDA, allocations do runner, geração, referência CPU, comparação e impressão ficam fora do total.
Allocations feitas pelo participante dentro das funções ficam dentro do total e podem afetar o intervalo de eventos.
Documente-as; não subtraia kernel de total para chamar o restante de transferência.
