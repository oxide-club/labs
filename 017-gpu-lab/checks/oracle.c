/* SPDX-License-Identifier: MIT */
#include "../materials/oracle.h"
#include <stdio.h>
#include <stdlib.h>
int main(void) {
    const size_t n = MAX_N;
    long long *a = malloc(n * sizeof(*a)), *b = malloc(n * sizeof(*b));
    long long *out = malloc(n * sizeof(*out));
    if (!a || !b || !out) { free(a); free(b); free(out); return 1; }
    int failed = 0;
    for (int sign = -1; sign <= 1; sign += 2) {
        for (size_t i = 0; i < n; ++i) a[i] = b[i] = sign * 1024;
        if (oracle(a,b,out,n) != sign * 4294968320LL) failed = 1;
        for (size_t i = 0; i < n; ++i) if (out[i] != sign * 2048) failed = 1;
    }
    free(a); free(b); free(out);
    if (!failed) puts("CPU: extremos positivos e negativos de 64 bits passaram.");
    return failed;
}
