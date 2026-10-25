/* SPDX-License-Identifier: MIT */
#include "counter.h"
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdlib.h>

typedef struct {
    CounterMode mode;
    unsigned iterations;
    uint64_t plain;
    atomic_uint_least64_t atomic;
    pthread_mutex_t lock;
} Context;

static void *worker(void *arg) {
    Context *c = arg;
    for (unsigned i = 0; i < c->iterations; ++i) {
        switch (c->mode) {
        case COUNTER_UNSAFE:
            /* Defeito intencional: data race em C causa UB. */
            c->plain++;
            break;
        case COUNTER_MUTEX:
            /* TODO: incremento protegido por mutex. */
            break;
        case COUNTER_ATOMIC:
            /* TODO: incremento por operação atômica C11. */
            break;
        }
    }
    return NULL;
}

int counter_run(CounterMode mode, unsigned threads, unsigned iterations, uint64_t *out) {
    if (!out || threads < 1 || threads > 32 || iterations > 1000000 ||
        mode < COUNTER_UNSAFE || mode > COUNTER_ATOMIC) return EINVAL;
    Context c = { .mode = mode, .iterations = iterations, .plain = 0 };
    atomic_init(&c.atomic, 0);
    int error = pthread_mutex_init(&c.lock, NULL);
    if (error) return error;
    pthread_t ids[32];
    unsigned made = 0;
    for (; made < threads; ++made) {
        error = pthread_create(&ids[made], NULL, worker, &c);
        if (error) break;
    }
    for (unsigned i = 0; i < made; ++i) {
        /* Join inválido seria defeito interno: não retornar com stack em uso. */
        if (pthread_join(ids[i], NULL)) abort();
    }
    if (!error) *out = mode == COUNTER_ATOMIC ? atomic_load(&c.atomic) : c.plain;
    if (pthread_mutex_destroy(&c.lock)) abort();
    return error;
}
