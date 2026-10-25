/* SPDX-License-Identifier: MIT */
#include "arena.h"
#include <stdint.h>
#include <stdio.h>
static unsigned checks, failures;
#define CHECK(x) do { ++checks; if (!(x)) { ++failures; fprintf(stderr, "linha %d: %s\n", __LINE__, #x); } } while (0)
static int start(Arena *a, size_t capacity) {
    int ok = arena_init(a, capacity);
    CHECK(ok);
    if (!ok) { CHECK(!a->base && !a->capacity && !a->used); return 0; }
    CHECK(a->base && a->capacity == capacity && a->used == 0);
    return a->base != NULL;
}
static void reject(Arena *a, size_t size, size_t alignment) {
    unsigned char *base = a->base;
    size_t used = a->used, capacity = a->capacity;
    CHECK(arena_alloc(a, size, alignment) == NULL);
    CHECK(a->used == used && a->capacity == capacity && a->base == base);
}
int main(void) {
    Arena a = {0};
    CHECK(!arena_init(&a, 0));
    CHECK(!a.base && !a.capacity && !a.used);
    arena_reset(&a); arena_destroy(&a); arena_destroy(&a);
    CHECK(!a.base && !a.capacity && !a.used);
    if (start(&a, 64)) {
        CHECK(arena_alloc(&a, 3, 1) == a.base);
        CHECK(arena_alloc(&a, 5, 1) == a.base + 3);
        CHECK(a.used == 8);
        reject(&a, 0, 1); reject(&a, 1, 0); reject(&a, 1, 3);
        reject(&a, 1, 6); reject(&a, 1, 12);
        reject(&a, 1, _Alignof(max_align_t) * 2);
        reject(&a, SIZE_MAX, 1); reject(&a, SIZE_MAX, _Alignof(max_align_t));
        reject(&a, 57, 1);
        CHECK(arena_alloc(&a, 1, 1) == a.base + 8);
        unsigned char *original_base = a.base;
        arena_reset(&a);
        CHECK(a.used == 0 && a.capacity == 64 && a.base == original_base);
        CHECK(arena_alloc(&a, 64, 1) == a.base);
        CHECK(a.used == 64); reject(&a, 1, 1);
    }
    arena_destroy(&a); arena_destroy(&a);
    CHECK(!a.base && !a.capacity && !a.used);
    if (start(&a, 4 * sizeof(max_align_t) + 64)) {
        CHECK(arena_alloc(&a, 1, 1) == a.base);
        void *result = arena_alloc(&a, sizeof(long double), _Alignof(long double));
        unsigned char *expected = a.base + _Alignof(long double);
        CHECK(result == expected);
        CHECK(a.used == _Alignof(long double) + sizeof(long double));
        /* A igualdade confirma a posição antes de subtrair ou acessar o objeto. */
        if (result == expected) {
            size_t offset = expected - a.base;
            long double *p = result;
            CHECK((uintptr_t)p % _Alignof(long double) == 0);
            *p = 1.25L;
            CHECK(*p == 1.25L);
            printf("long double: sizeof=%zu alignment=%zu offset=%zu\n", sizeof *p, _Alignof(long double), offset);
        }
        arena_reset(&a);
        /* Só ponteiros novos são usados após reset. */
        CHECK(arena_alloc(&a, 1, 1) == a.base);
    }
    arena_destroy(&a);
    for (size_t alignment = 1; alignment <= _Alignof(max_align_t); alignment *= 2) {
        if (start(&a, 64)) {
            CHECK(arena_alloc(&a, 1, 1) == a.base);
            unsigned char *p = arena_alloc(&a, 1, alignment);
            CHECK(p == a.base + alignment);
            CHECK(a.used == alignment + 1);
            if (p == a.base + alignment) { a.base[0] = 0xA5; *p = 0x5A; CHECK(a.base[0] == 0xA5); }
        }
        arena_destroy(&a);
        if (start(&a, alignment)) {
            CHECK(arena_alloc(&a, 1, 1) == a.base);
            reject(&a, 1, alignment); /* Inclua padding no consumo; alignment=1 já esgotou a região. */
        }
        arena_destroy(&a);
    }
    if (start(&a, 64)) {
        unsigned char *blocks[64] = {0};
        for (size_t i = 0; i < 64; ++i) {
            blocks[i] = arena_alloc(&a, 1, 1);
            CHECK(blocks[i] == a.base + i);
            CHECK(a.used == i + 1 && a.used <= a.capacity);
            if (blocks[i] == a.base + i) *blocks[i] = (unsigned char)i;
        }
        reject(&a, 1, 1);
        for (size_t i = 0; i < 64; ++i)
            if (blocks[i] == a.base + i) CHECK(*blocks[i] == (unsigned char)i);
    }
    arena_destroy(&a);
    printf("%u verificacoes; %u falhas\n", checks, failures);
    return failures != 0;
}
