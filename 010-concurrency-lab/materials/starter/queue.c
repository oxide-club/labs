/* SPDX-License-Identifier: MIT */
#include "queue.h"
#include <errno.h>
/* ENOSYS identifica somente o starter; não é resultado do contrato final. */
int queue_init(Queue *q, size_t capacity) {
    (void)q; (void)capacity;
    /* TODO: validação, estado inicial e rollback de primitivas parciais. */
    return ENOSYS;
}
int queue_push(Queue *q, uint64_t id) {
    (void)q; (void)id;
    /* TODO: exclusão, espera, inserção e notificação. */
    return ENOSYS;
}
int queue_pop(Queue *q, uint64_t *out) {
    (void)q; (void)out;
    /* TODO: exclusão, espera, retirada e notificação. */
    return ENOSYS;
}
int queue_close(Queue *q) {
    (void)q;
    /* TODO: fechamento idempotente e wakeups. */
    return ENOSYS;
}
int queue_destroy(Queue *q) {
    (void)q;
    /* TODO: liberar primitivas após todas as threads terminarem. */
    return ENOSYS;
}
