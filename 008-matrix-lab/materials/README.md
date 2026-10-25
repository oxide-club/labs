# Materiais e contrato numérico

Leia este contrato antes de editar `starter/matrix.c`. `matrix.h` fixa a API C11.
As três funções recebem `(m,k,n,a,b,c,tile)` e calculam **C=A×B**:
A tem m×k valores, B tem k×n e C tem m×n. Arrays contíguos em ordem de linhas
(row-major): A[i*k+q], B[q*n+j], C[i*n+j]. Não há transposição nem padding.
O valor inicial de C deve ser ignorado. A e B não podem mudar.

## Valores e limites

- Ambiente: Linux, C11, `double` IEEE 754 binary64, `size_t` com pelo menos 32 bits.
- Cada dimensão deve estar em 1..4096; `tile` em 1..256, inclusive nas variantes sem blocking.
- Rejeite dimensões antes de multiplicar tamanhos ou formar ponteiros. Cada produto de contagens e bytes deve caber em `SIZE_MAX`; verifique antes de calcular.
- Os três ponteiros devem ser não nulos. O chamador garante buffers com as contagens exigidas, alinhamento para double e ausência de overlap. A API não consegue verificar comprimentos reais nem ponteiros inválidos.
- Cada entrada de A e B deve ser finita e estar em [-16,16]. Verifique todas as entradas antes de escrever C. Assim cada soma exata tem módulo no máximo 4096×256=1048576; não se exige tratamento de overflow numérico fora desse domínio.
- Retorne `MATRIX_OK` (0) no sucesso; `MATRIX_INVALID` (1) para dimensão, tile, ponteiro nulo ou valor fora do domínio. Em erro, preserve C integralmente. Não faça allocation de memória na função; buffers pertencem ao chamador.
- `MATRIX_TODO` (2) existe apenas no starter incompleto e não satisfaz o contrato final.
- Para cada elemento, exija `abs(obtido-referencia) <= 1e-6 + 1e-10*abs(referencia)` e saída finita. O oráculo acumula em long double; plataformas em que este tipo equivale a double continuam aceitas, com menor independência numérica. A parcela absoluta 1e-6 cobre inclusive cancelamento: o limite conservador gamma_(2k)×k×256 fica abaixo de 1e-6 para k<=4096 e epsilon de arredondamento 2^-53. A parcela relativa 1e-10 permite comparação proporcional. A tolerância cobre erros de soma binary64 neste domínio, sem exigir igualdade bit a bit entre ordens. Não use `-ffast-math` no núcleo.
- Implemente as variantes ijk, ikj e blocking com tails corretas quando tile não divide dimensões. Todas continuam com custo aritmético O(mkn). Não há requisito universal de aceleração.

## Arquivos

`starter/matrix.c` contém somente lacunas. `../checks/check.c` inclui a fixture manual
2×3 por 3×2: A=[1,2,3;4,5,6], B=[7,8;9,10;11,12], C=[58,64;139,154].
Outros casos usam 3×5 por 5×7, tiles 1..8 e entradas inválidas. Antes de cada tile, C recebe NAN para impedir que resultados anteriores ocultem tails omitidas. Os checks também comparam A/B com cópias e exigem preservação integral de C quando o último elemento de A ou B é inválido. Os dados estão no check,
com licença CC0 para os valores; código MIT. `../checks/oracle.h` fornece somente a referência
escalar para conferir resultados; não substitui as três implementações do participante.
`../experiments/benchmark.c` gera dados e mede as implementações depois de validar.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** Livre sob restrições algorítmicas; por exemplo C, Rust, C++ e Python.

**Linguagens recomendadas:** Rust, C++ e Python.

**Restrições técnicas e plataforma:** Arrays contíguos row-major binary64; ijk, ikj e blocking próprios; sem BLAS/NumPy no núcleo.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve dimensões 1..4096, tile 1..256, entradas finitas [-16,16], saídas sobrescritas e entradas intactas. Erro preserva C. Use abs(erro) <= 1e-6 + 1e-10*abs(referência), sem fast-math ou arredondamento textual intermediário. Verifique produtos de tamanhos antes de allocation. Python pode usar array de doubles e loops explícitos; listas de objetos são comparação de layout, não substituem a investigação de arrays contíguos. Não há garantia de aceleração.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
