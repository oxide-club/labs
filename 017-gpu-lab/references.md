# Referências orientadas

Consulta em 25/10/2026. As fontes abaixo não foram copiadas para o pacote.

## Modelo e medição

- [NVIDIA CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html): documentação primária verificada. Leia modelo de execução, hierarquia de memória, SIMT e execução assíncrona. Pergunta: qual barrier coordena threads de um bloco e por que ela não coordena toda a grade?
- [NVIDIA CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html): documentação primária verificada. Observe verificação de erros, eventos, memória e custo de transferência. Pergunta: quando uma operação rápida no dispositivo continua lenta de ponta a ponta?

## Código real, após o núcleo

- [NVIDIA CUDA Samples: vectorAdd.cu](https://github.com/NVIDIA/cuda-samples/blob/5443602d89ed99aede2e4b7bf329daddeadb320e/cpp/0_Introduction/vectorAdd/vectorAdd.cu): arquivo e mecanismo verificados. Mostra índice global, teste de limite, `cudaMallocManaged`, kernel launch e `cudaDeviceSynchronize`. Usa memória unificada, sem `cudaMemcpy` explícito nem tratamento completo dos erros de API; compare essas escolhas com o runner deste laboratório. Diferentemente deste laboratório, usa ponto flutuante e uma única operação. Pergunta: onde o host pode observar um erro de execução assíncrono?
- [NVIDIA CUDA Samples: reduction_kernel.cu](https://github.com/NVIDIA/cuda-samples/blob/5443602d89ed99aede2e4b7bf329daddeadb320e/cpp/2_Concepts_and_Techniques/reduction/reduction_kernel.cu): arquivo e variantes de reduction verificados. Observe memória compartilhada, sincronização, transformações de acesso e hipóteses dos tamanhos de bloco. O arquivo oferece otimizações posteriores ao núcleo; não substitui sua explicação de blocos parciais. Pergunta: qual hipótese de uma variante deixa de valer em um tail?

Os dois arquivos foram conferidos no commit `5443602d89ed99aede2e4b7bf329daddeadb320e`. Consulte também [escrita de kernels](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-cuda-kernels.html) e [execução assíncrona](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/asynchronous-execution.html).
