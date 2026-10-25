/* SPDX-License-Identifier: MIT */
#ifndef ARENA_H
#define ARENA_H
#include <stdbool.h>
#include <stddef.h>
typedef struct {
    unsigned char *base;
    size_t capacity;
    size_t used;
} Arena;
bool arena_init(Arena *a, size_t capacity);
void *arena_alloc(Arena *a, size_t size, size_t alignment);
void arena_reset(Arena *a);
void arena_destroy(Arena *a);
#endif
