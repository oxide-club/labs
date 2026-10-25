# Materiais e execução

`kernels.cu` contém as duas funções incompletas. `kernels.h` fixa a interface.
`runner.cu` fornece preparação CUDA, comparação CPU e temporização.
`oracle.c` contém apenas a referência sequencial e o gerador. `cpu.c` permite verificá-los sem CUDA.
O [contrato](contract.md) define entradas, erros, sincronização e escopo dos tempos.

A partir da raiz do laboratório:

```sh
make -C materials cpu
python3 checks/check.py
make -C materials gpu
materials/build/probe
python3 checks/check.py --gpu
```

O primeiro build usa C11. O segundo usa CUDA C++14 e exige `nvcc` no PATH.
Se a GPU exigir uma arquitetura explícita, registre a alteração nas flags do Makefile.
Não interprete ausência de `nvcc` como falha do participante.
Não há instalação automática de compilador ou driver.

Para examinar um caso pequeno CPU:

```sh
materials/build/cpu 3 0
```

A primeira linha contém a soma de `a`; a segunda contém o vetor `a+b`.
O resultado normativo é `-3021`, seguido de `-2048 -2000 -1952`.
Uma execução GPU equivalente usa `materials/build/gpu 3 64 0` e publica CSV somente se os resultados conferirem.
O runner usa buffers distintos. Todas as operações devem usar o stream padrão.

`materials/build/probe` verifica dispositivo, runtime, allocation e cópias, sem executar kernels próprios.
Seu sucesso verifica apenas essa infraestrutura; não valida o exercício nem produz medição.

Para verificar os extremos de 64 bits em entradas constantes:

```sh
materials/build/cpu 65 0 positive
materials/build/cpu 65 0 negative
materials/build/gpu 4194305 64 0 positive
materials/build/gpu 4194305 64 0 negative
```

Os checks repetem os dois extremos GPU para todos os blocos aceitos.
No tamanho máximo, exigem reduction ±4294968320 e vetor ±2048.
O modo padrão continua usando o gerador periódico dos datasets de medição.

## Linguagens e ambiente

**Linguagem de referência:** C (CPU) e CUDA C++ (GPU).

**Linguagens aceitas:** Tecnologias com compute real; por exemplo CUDA C++, HIP C++ e WGSL com Rust.

**Linguagens recomendadas:** CUDA C++, HIP C++ e WGSL com Rust.

**Restrições técnicas e plataforma:** Dispositivo compute real; CUDA exige Toolkit/runtime/driver/GPU compatíveis.

**Tipo de equivalência:** equivalente sob contrato adaptado; CPU apenas comparativa.

### Contrato independente da linguagem

Preserve device pointers, kernels próprios, soma e reduction no dispositivo. Inteiros com sinal de 64 bits, entradas [-1024,1024] e n<=4194305; comparação exata e overflow excluído pelos limites. Blocos 64/128/256/512, tail sizes, barriers e todas as passagens importam. HIP/WebGPU são aceitos sob adaptação, mas não têm starter oficial. Uma plataforma sem int64 deve demonstrar representação equivalente, sem reduzir o domínio.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Materiais oficiais:** referência C para CPU e starter CUDA C++. Compilação CUDA, probe, checks GPU e medição foram executados em 25/10/2026 na RTX 4060, com nvcc 13.4 e driver 615.78.08. Uma implementação privada passou; o starter mantém os TODOs. Veja o registro de preparação.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

O modo de fixture `ramp` usa `a[i]=b[i]=1024-(i mod 7)`; em `n=4194305`,
a soma exata é 4282385411. Execute `materials/build/gpu 4194305 64 0 ramp`.
O padding com sentinel verifica escritas após `n`; ele é inicializado e lido fora
dos intervalos medidos. H2D mede somente os dois vetores de `n` elementos; D2H mede
o vetor lógico e o escalar da reduction. Nenhum padding entra nos bytes transferidos
publicados; a verificação de sentinels ocorre depois do fim da medição.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
