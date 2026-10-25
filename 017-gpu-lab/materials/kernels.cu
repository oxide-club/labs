/* SPDX-License-Identifier: MIT */
#include "kernels.h"
cudaError_t launch_add(const long long *a, const long long *b, long long *out,
                       size_t n, unsigned block) {
    // TODO: kernel, índice global, proteção do tail e kernel launch no stream padrão.
    (void)a; (void)b; (void)out; (void)n; (void)block;
    return cudaErrorNotSupported;
}
cudaError_t launch_reduce(const long long *a, long long *out, size_t n, unsigned block) {
    // TODO: reduction paralela na GPU, memória compartilhada, barriers e passagens.
    // n == 0 deve produzir zero. Não leia a entrada nem lance uma grade vazia.
    // Todo scratch próprio deve ser liberado mesmo se uma operação CUDA falhar.
    (void)a; (void)out; (void)n; (void)block;
    return cudaErrorNotSupported;
}
