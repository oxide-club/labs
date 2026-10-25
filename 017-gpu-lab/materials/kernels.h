/* SPDX-License-Identifier: MIT */
#ifndef GPU_KERNELS_H
#define GPU_KERNELS_H
#include <cuda_runtime.h>
#include <stddef.h>
cudaError_t launch_add(const long long *, const long long *, long long *, size_t, unsigned);
cudaError_t launch_reduce(const long long *, long long *, size_t, unsigned);
#endif
