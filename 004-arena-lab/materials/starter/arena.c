/* SPDX-License-Identifier: MIT */
#include "arena.h"
#include <stdlib.h>
bool arena_init(Arena *a, size_t capacity) {
    /* TODO: reserve a região e publique o estado somente no sucesso. */
    (void)a;
    (void)capacity;
    return false;
}
void *arena_alloc(Arena *a, size_t size, size_t alignment) {
    /* TODO: valide, calcule o consumo seguro e só então altere o estado. */
    (void)a;
    (void)size;
    (void)alignment;
    return NULL;
}
void arena_reset(Arena *a) {
    /* TODO: implemente o reset lógico. */
    (void)a;
}
void arena_destroy(Arena *a) {
    free(a->base);
    *a = (Arena){0};
}
