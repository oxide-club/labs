/* SPDX-License-Identifier: MIT */
#ifndef GPU_ORACLE_H
#define GPU_ORACLE_H
#include <stddef.h>
#define MAX_N 4194305u
#ifdef __cplusplus
extern "C" {
#endif
void generate(long long *a, long long *b, size_t n, unsigned seed);
long long oracle(const long long *a, const long long *b, long long *out, size_t n);
#ifdef __cplusplus
}
#endif
#endif
