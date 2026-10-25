/* SPDX-License-Identifier: MIT */
#include "oracle.h"
#include <limits.h>
#if defined(__cplusplus)
static_assert(LLONG_MAX == 9223372036854775807LL, "long long deve ter 64 bits");
#else
_Static_assert(LLONG_MAX == 9223372036854775807LL, "long long deve ter 64 bits");
#endif
void generate(long long *a, long long *b, size_t n, unsigned seed) {
    for (size_t i = 0; i < n; ++i) {
        a[i] = (long long)((i * 17u + seed) % 2049u) - 1024;
        b[i] = (long long)((i * 31u + seed * 3u) % 2049u) - 1024;
    }
}
long long oracle(const long long *a, const long long *b, long long *out, size_t n) {
    long long sum = 0;
    for (size_t i = 0; i < n; ++i) { out[i] = a[i] + b[i]; sum += a[i]; }
    return sum;
}
