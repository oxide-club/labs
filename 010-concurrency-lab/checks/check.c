/* SPDX-License-Identifier: MIT */
#define _POSIX_C_SOURCE 200809L
#include "counter.h"
#include "queue.h"
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define CHECK(test) do { if (!(test)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #test); exit(1); } } while (0)
/* Falha do harness encerra o processo inteiro, inclusive suas threads. */
static void join(pthread_t t) { CHECK(pthread_join(t, NULL) == 0); }
static void start(pthread_t *t, void *(*fn)(void *), void *arg) {
    CHECK(pthread_create(t, NULL, fn, arg) == 0);
}
static void pause_briefly(void) {
    struct timespec delay = { .tv_sec = 0, .tv_nsec = 50000000 };
    while (nanosleep(&delay, &delay) && errno == EINTR) {}
}
static void counter_check(CounterMode mode) {
    const unsigned threads[] = {1, 2, 7, 32};
    const unsigned counts[] = {0, 1, 193, 10000};
    for (unsigned t = 0; t < 4; ++t) {
        for (unsigned n = 0; n < 4; ++n) {
            uint64_t out = UINT64_MAX;
            CHECK(counter_run(mode, threads[t], counts[n], &out) == 0);
            CHECK(out == (uint64_t)threads[t] * counts[n]);
        }
    }
    uint64_t out = 0;
    CHECK(counter_run(mode, 1, 1000000, &out) == 0);
    CHECK(out == 1000000);
    CHECK(counter_run(mode, 8, 1000000, &out) == 0);
    CHECK(out == 8000000);
}
static void invalid(void) {
    uint64_t out = 123;
    CHECK(counter_run(COUNTER_MUTEX, 0, 1, &out) == EINVAL);
    CHECK(counter_run(COUNTER_ATOMIC, 33, 1, &out) == EINVAL);
    CHECK(counter_run(COUNTER_MUTEX, 1, 1000001, &out) == EINVAL);
    CHECK(counter_run((CounterMode)99, 1, 1, &out) == EINVAL);
    CHECK(counter_run((CounterMode)-1, 1, 1, &out) == EINVAL);
    CHECK(counter_run(COUNTER_MUTEX, 1, 1, NULL) == EINVAL);
    CHECK(out == 123);
    Queue q;
    CHECK(queue_init(NULL, 1) == EINVAL);
    CHECK(queue_init(&q, 0) == EINVAL);
    CHECK(queue_init(&q, 65) == EINVAL);
    CHECK(queue_init(&q, SIZE_MAX) == EINVAL);
    CHECK(queue_push(NULL, 1) == EINVAL);
    CHECK(queue_pop(NULL, &out) == EINVAL);
    CHECK(queue_close(NULL) == EINVAL);
    CHECK(queue_destroy(NULL) == EINVAL);
    CHECK(queue_init(&q, 1) == 0);
    CHECK(queue_pop(&q, NULL) == EINVAL);
    CHECK(queue_close(&q) == 0);
    CHECK(queue_destroy(&q) == 0);
}
static void fifo(void) {
    Queue q;
    CHECK(queue_init(&q, 3) == 0);
    const uint64_t values[] = {0, UINT64_MAX, 17};
    for (unsigned round = 0; round < 20; ++round) {
        for (unsigned i = 0; i < 3; ++i) CHECK(queue_push(&q, values[i]) == 0);
        for (unsigned i = 0; i < 3; ++i) {
            uint64_t out = 99;
            CHECK(queue_pop(&q, &out) == 0);
            CHECK(out == values[i]);
        }
    }
    CHECK(queue_push(&q, 42) == 0);
    CHECK(queue_push(&q, 43) == 0);
    CHECK(queue_close(&q) == 0);
    CHECK(queue_close(&q) == 0);
    CHECK(queue_push(&q, 44) == EPIPE);
    uint64_t out = 0;
    CHECK(queue_pop(&q, &out) == 0 && out == 42);
    CHECK(queue_pop(&q, &out) == 0 && out == 43);
    CHECK(queue_pop(&q, &out) == ENODATA && out == 43);
    CHECK(queue_destroy(&q) == 0);
    CHECK(queue_init(&q, 1) == 0); /* Reutilização após destroy. */
    CHECK(queue_close(&q) == 0);
    CHECK(queue_pop(&q, &out) == ENODATA && out == 43);
    CHECK(queue_destroy(&q) == 0);
}

typedef struct {
    Queue *q;
    int push, result;
    uint64_t value;
    atomic_bool entered, done;
} One;
static void *one(void *arg) {
    One *a = arg;
    atomic_store(&a->entered, 1);
    a->result = a->push ? queue_push(a->q, a->value) : queue_pop(a->q, &a->value);
    atomic_store(&a->done, 1);
    return NULL;
}
static void blocking(int full, int closing) {
    Queue q;
    CHECK(queue_init(&q, 1) == 0);
    if (full) CHECK(queue_push(&q, 91) == 0);
    const unsigned n = closing ? 4 : 1;
    One args[4]; pthread_t ids[4];
    for (unsigned i = 0; i < n; ++i) {
        args[i].q = &q; args[i].push = full;
        args[i].value = 92; args[i].result = -1;
        atomic_init(&args[i].entered, 0); atomic_init(&args[i].done, 0);
        start(&ids[i], one, &args[i]);
    }
    for (unsigned i = 0; i < n; ++i)
        while (!atomic_load(&args[i].entered)) pause_briefly();
    /* Janela de observação, não prova de que entrou em cond_wait. */
    pause_briefly();
    for (unsigned i = 0; i < n; ++i) CHECK(!atomic_load(&args[i].done));
    uint64_t out = 0;
    if (closing) CHECK(queue_close(&q) == 0);
    else if (full) CHECK(queue_pop(&q, &out) == 0 && out == 91);
    else CHECK(queue_push(&q, 90) == 0);
    for (unsigned i = 0; i < n; ++i) {
        join(ids[i]);
        CHECK(args[i].result == (closing ? (full ? EPIPE : ENODATA) : 0));
        if (!full) CHECK(args[i].value == (closing ? 92 : 90));
    }
    if (full) CHECK(queue_pop(&q, &out) == 0 && out == (closing ? 91 : 92));
    CHECK(queue_close(&q) == 0);
    CHECK(queue_pop(&q, &out) == ENODATA);
    CHECK(queue_destroy(&q) == 0);
}

typedef struct { Queue *q; unsigned producer, count; } Producer;
typedef struct { Queue *q; unsigned total; atomic_uint *seen; } Consumer;
static void *produce(void *arg) {
    Producer *p = arg;
    for (unsigned i = 0; i < p->count; ++i)
        CHECK(queue_push(p->q, (uint64_t)p->producer * p->count + i) == 0);
    return NULL;
}
static void *consume(void *arg) {
    Consumer *c = arg;
    for (;;) {
        uint64_t id = UINT64_MAX;
        int result = queue_pop(c->q, &id);
        if (result == ENODATA) { CHECK(id == UINT64_MAX); break; }
        CHECK(result == 0);
        CHECK(id < c->total);
        CHECK(atomic_fetch_add(&c->seen[id], 1) == 0);
    }
    return NULL;
}
static void stress(unsigned cap, unsigned p, unsigned c, unsigned count) {
    CHECK(cap >= 1 && cap <= 64 && p >= 1 && p <= 8 && c >= 1 && c <= 8 && count <= 10000);
    unsigned total = p * count;
    atomic_uint *seen = calloc(total ? total : 1, sizeof(*seen));
    CHECK(seen != NULL);
    for (unsigned i = 0; i < total; ++i) atomic_init(&seen[i], 0);
    Queue q; CHECK(queue_init(&q, cap) == 0);
    Producer args[8]; Consumer receiver = {&q, total, seen};
    pthread_t producers[8], consumers[8];
    for (unsigned i = 0; i < c; ++i) start(&consumers[i], consume, &receiver);
    for (unsigned i = 0; i < p; ++i) {
        args[i] = (Producer){&q, i, count};
        start(&producers[i], produce, &args[i]);
    }
    for (unsigned i = 0; i < p; ++i) join(producers[i]);
    CHECK(queue_close(&q) == 0);
    for (unsigned i = 0; i < c; ++i) join(consumers[i]);
    for (unsigned i = 0; i < total; ++i) CHECK(atomic_load(&seen[i]) == 1);
    CHECK(queue_destroy(&q) == 0);
    free(seen);
}
int main(int argc, char **argv) {
    if (argc == 2 && !strcmp(argv[1], "mutex")) counter_check(COUNTER_MUTEX);
    else if (argc == 2 && !strcmp(argv[1], "atomic")) counter_check(COUNTER_ATOMIC);
    else if (argc == 2 && !strcmp(argv[1], "invalid")) invalid();
    else if (argc == 2 && !strcmp(argv[1], "fifo")) fifo();
    else if (argc == 2 && !strcmp(argv[1], "empty")) blocking(0, 0);
    else if (argc == 2 && !strcmp(argv[1], "full")) blocking(1, 0);
    else if (argc == 2 && !strcmp(argv[1], "close-empty")) blocking(0, 1);
    else if (argc == 2 && !strcmp(argv[1], "close-full")) blocking(1, 1);
    else if (argc == 6 && !strcmp(argv[1], "stress"))
        stress((unsigned)atoi(argv[2]), (unsigned)atoi(argv[3]), (unsigned)atoi(argv[4]), (unsigned)atoi(argv[5]));
    else return 2;
    puts("PASS");
    return 0;
}
