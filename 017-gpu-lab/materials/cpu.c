/* SPDX-License-Identifier: MIT */
#include "oracle.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc != 3 && argc != 4) return 2;
    int mode = 0;
    if (argc == 4) {
        if (strcmp(argv[3], "positive") == 0) mode = 1;
        else if (strcmp(argv[3], "negative") == 0) mode = -1;
        else if (strcmp(argv[3], "ramp") == 0) mode = 2;
        else return 2;
    }
    char *end; unsigned long n = strtoul(argv[1], &end, 10);
    if (!*argv[1] || *end || n > MAX_N || argv[1][0] == '-') return 2;
    unsigned long seed = strtoul(argv[2], &end, 10);
    if (!*argv[2] || *end || seed > 1000 || argv[2][0] == '-') return 2;
    size_t count = n ? n : 1;
    long long *a = calloc(count, sizeof(*a)), *b = calloc(count, sizeof(*b));
    long long *out = calloc(count, sizeof(*out));
    if (!a || !b || !out) { free(a); free(b); free(out); return 1; }
    if (mode) {
        for (size_t i = 0; i < n; ++i) a[i] = b[i] = mode == 2 ? 1024LL - (long long)(i % 7) : mode * 1024LL;
    } else generate(a, b, n, (unsigned)seed);
    long long sum = oracle(a, b, out, n);
    printf("%lld\n", sum);
    for (size_t i = 0; i < n; ++i) printf("%lld%c", out[i], i + 1 == n ? '\n' : ' ');
    free(a); free(b); free(out); return 0;
}
