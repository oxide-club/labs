# Medir depois de verificar

1. Preveja a sequência de índices de A, B e C para cada ordem de loops. Estime o conjunto de dados: `8*(m*k+k*n+m*n)` bytes; o benchmark também mantém os três buffers durante a referência.
2. Identifique CPU e cache com `lscpu` e, se disponível, `/sys/devices/system/cpu/cpu0/cache/`. Escolha um caso cujo conjunto caiba na cache relevante e outro que a exceda. Declare qual nível de cache comparou. Ajuste tamanhos ao hardware e ao tempo disponível, dentro do limite 4096; não suponha que um tamanho fixo exceda toda cache.
3. Execute os checks antes de medir. Compile conforme o README, sem sanitizers. Declare a versão exata do compilador em `MATRIX_COMPILER`, flags em `MATRIX_FLAGS` e CPU/cache/SO em `MATRIX_HARDWARE`. Esses campos são obrigatórios; não inclua aspas ou quebras de linha.

Exemplo de comando (substitua os metadados pelos valores reais):

```sh
MATRIX_COMPILER='cc versão observada' MATRIX_FLAGS='-std=c11 -O2 -Wall -Wextra -Wpedantic' MATRIX_HARDWARE='CPU e cache observadas; Linux' /tmp/matrix-benchmark 31 47 29 8 42 2 7 > /tmp/matrix-small.csv
```

A CLI recebe M K N TILE SEED WARMUPS REPS, somente sequências não vazias de dígitos ASCII 0..9, sem sinais, espaços ou sufixos.
Limites: dimensões 1..4096, tile 1..256, seed 0..4294967295, warmups 1..100,
repetições 3..1000. Uso/metadados/allocation inválidos retornam 2; validação falha retorna 1.
Não aloque um caso grande sem estimar RAM e tempo (a referência é O(mkn)).
O gerador LCG uint32 usa `state=1664525*state+1013904223` módulo 2³² e produz
`((state%2049)-1024)/1024`; a seed fixa os mesmos dados para todas as variantes.

O CSV só começa após validar as três variantes. Há warmups por variante, e cada amostra
mede apenas uma chamada da função com CLOCK_MONOTONIC. Validação de argumentos e entradas
feita pela implementação pertence à chamada e fica no tempo. Allocation, geração, referência,
validação da saída e I/O ficam fora. A validação pós-amostra ocorre antes da próxima medida;
essa atividade aquece caches. Antes de cada chamada validada e de cada amostra, o driver preenche C com NAN fora do intervalo cronometrado. Essa escrita também aquece a cache e garante que valores antigos não ocultem saídas incompletas: declare essas limitações. A ordem é ijk, ikj, blocked e cada
chamada deve sobrescrever C. Registre governador, carga concorrente e afinidade quando conhecidos.

4. Varie tile (por exemplo 8, 16, 32) e inclua pelo menos um caso retangular com tails.
Mantenha seed, flags, dimensões e threads=1 iguais na comparação. Repita sessões alternando
ordem em uma cópia do driver para investigar viés de aquecimento/frequência, registrando a alteração.
5. Guarde CSV bruto e calcule mediana, mínimo e dispersão por variante. Explique resultados
sem limiar universal de tempo. Diferencie hipótese de localidade de evidência: tempo sozinho
não identifica cache misses. `perf stat` é opcional e depende das permissões locais.
