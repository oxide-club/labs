/* SPDX-License-Identifier: MIT */
#ifndef QUEUE_H
#define QUEUE_H
#include <pthread.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define QUEUE_MAX_CAPACITY 64
/* Pode adaptar campos internos, preservando API e capacidade. */
typedef struct {
    uint64_t items[QUEUE_MAX_CAPACITY];
    size_t capacity, head, tail, count;
    bool closed;
    pthread_mutex_t lock;
    pthread_cond_t not_empty, not_full;
} Queue;
int queue_init(Queue *q, size_t capacity);
int queue_push(Queue *q, uint64_t id);
int queue_pop(Queue *q, uint64_t *out);
int queue_close(Queue *q);
int queue_destroy(Queue *q);
#endif
