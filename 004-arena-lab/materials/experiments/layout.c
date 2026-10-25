/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int main(void) {
    void *p = malloc(64);
    if (!p) return 1;
    printf("long double: sizeof=%zu alignment=%zu\n", sizeof(long double), _Alignof(long double));
    printf("max_align_t: alignment=%zu; resto da base=%zu\n", _Alignof(max_align_t), (size_t)((uintptr_t)p % _Alignof(max_align_t)));
    free(p);
    return 0;
}
