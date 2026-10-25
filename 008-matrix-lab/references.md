# Referências orientadas

Consulta em 25/10/2026. Os dois arquivos OpenBLAS foram baixados e inspecionados no commit
`8795fc7985635de1ecf674b87e2008a15097ffab` (v0.3.29). Não copiamos fontes de terceiros.

- [OpenBLAS: level3.c](https://github.com/OpenMathLib/OpenBLAS/blob/8795fc7985635de1ecf674b87e2008a15097ffab/driver/level3/level3.c): organiza divisão em blocos, cópias e chamadas de kernel. Observe ICOPY_OPERATION, OCOPY_OPERATION e KERNEL_OPERATION. Diferentemente do exercício, combina packing e caminhos de biblioteca. Pergunta: por que separar packing do microkernel?
- [OpenBLAS: dgemm_kernel_4x8_haswell.S](https://github.com/OpenMathLib/OpenBLAS/blob/8795fc7985635de1ecf674b87e2008a15097ffab/kernel/x86_64/dgemm_kernel_4x8_haswell.S): microkernel específico de Haswell. Observe operações com registradores ymm. Diferentemente do núcleo C11, pressupõe arquitetura e dados preparados. Pergunta: quais valores permanecem nos registradores durante a acumulação?
- [CS:APP](https://csapp.cs.cmu.edu/3e/), capítulos 5 e 6: otimização e hierarquia de memória.
- [Zhirkov](https://link.springer.com/book/10.1007/978-1-4842-2403-8), capítulo 16: desempenho e SIMD.
- [Goldberg](https://docs.oracle.com/cd/E19957-01/816-2464/ncg_goldberg.html): arredondamento de ponto flutuante.
- [Linux: perf security](https://docs.kernel.org/admin-guide/perf-security.html): limites de acesso a contadores opcionais.

As leituras bibliográficas vêm do currículo; seus textos integrais não foram verificados
nesta preparação. Os arquivos de código foram verificados diretamente.
