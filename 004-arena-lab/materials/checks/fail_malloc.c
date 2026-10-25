/* SPDX-License-Identifier: MIT */
#include "arena.h"
#include <stdio.h>
void *__wrap_malloc(size_t size) { (void)size; return NULL; }
int main(void) {
    Arena a = {0};
    if (arena_init(&a, 64) || a.base || a.capacity || a.used) {
        fputs("falha de malloc alterou o estado\n", stderr); return 1;
    }
    arena_destroy(&a);
    puts("falha de malloc: estado zerado");
    return 0;
}
