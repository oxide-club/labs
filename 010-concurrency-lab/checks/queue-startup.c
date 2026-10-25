/* SPDX-License-Identifier: MIT */
#include "queue.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define REQUIRE(test) do { if (!(test)) { fprintf(stderr, "FAIL queue-startup line %d: %s\n", __LINE__, #test); exit(1); } } while (0)

typedef enum { MUTEX, CONDITION } Kind;
typedef struct { void *address; Kind kind; int initialized, destroyed; } Record;
static Record records[64];
static unsigned attempts, fail_at;
static int injected, error_code;
int __real_pthread_mutex_init(pthread_mutex_t *, const pthread_mutexattr_t *);
int __real_pthread_cond_init(pthread_cond_t *, const pthread_condattr_t *);
int __real_pthread_mutex_destroy(pthread_mutex_t *);
int __real_pthread_cond_destroy(pthread_cond_t *);

static Record *attempt(void *address, Kind kind) {
    REQUIRE(attempts < 64);
    Record *record = &records[attempts++];
    *record = (Record){address, kind, 0, 0};
    if (attempts == fail_at) injected = 1;
    return record;
}
int __wrap_pthread_mutex_init(pthread_mutex_t *lock, const pthread_mutexattr_t *attr) {
    Record *record = attempt(lock, MUTEX);
    if (attempts == fail_at) return error_code;
    int code = __real_pthread_mutex_init(lock, attr);
    REQUIRE(code == 0); /* Falha do ambiente, distinta da injeção deliberada. */
    record->initialized = 1;
    return code;
}
int __wrap_pthread_cond_init(pthread_cond_t *cond, const pthread_condattr_t *attr) {
    Record *record = attempt(cond, CONDITION);
    if (attempts == fail_at) return error_code;
    int code = __real_pthread_cond_init(cond, attr);
    REQUIRE(code == 0);
    record->initialized = 1;
    return code;
}
static Record *destroying(void *address, Kind kind) {
    for (unsigned i = attempts; i > 0; --i) {
        Record *record = &records[i - 1];
        if (record->address == address && record->kind == kind) {
            REQUIRE(record->initialized && !record->destroyed);
            return record;
        }
    }
    /* Inicializadores estáticos POSIX não passam pelos wrappers de init. */
    return NULL;
}
int __wrap_pthread_mutex_destroy(pthread_mutex_t *lock) {
    Record *record = destroying(lock, MUTEX);
    int code = __real_pthread_mutex_destroy(lock);
    REQUIRE(code == 0);
    if (record) record->destroyed = 1;
    return code;
}
int __wrap_pthread_cond_destroy(pthread_cond_t *cond) {
    Record *record = destroying(cond, CONDITION);
    int code = __real_pthread_cond_destroy(cond);
    REQUIRE(code == 0);
    if (record) record->destroyed = 1;
    return code;
}
static void reset(unsigned nth, int error) {
    memset(records, 0, sizeof records);
    attempts = 0; injected = 0; fail_at = nth; error_code = error;
}
static void cleaned(void) {
    for (unsigned i = 0; i < attempts; ++i)
        REQUIRE(records[i].destroyed == records[i].initialized);
}

static void queue_trials(int error) {
    /* Descobre tentativas pela execução, sem impor ordem mutex/condições. */
    for (unsigned nth = 1; nth <= 64; ++nth) {
        Queue queue;
        reset(nth, error);
        int result = queue_init(&queue, 3);
        if (injected) {
            REQUIRE(result == error);
            cleaned();
            printf("checked error=%d attempt=%u\n", error, nth);
        } else {
            REQUIRE(result == 0); /* Rejeita o starter ENOSYS. */
            REQUIRE(nth > attempts);
            if (!attempts) puts("OBS: inicialização estática; sem falhas dinâmicas para injetar");
            REQUIRE(queue_close(&queue) == 0);
            REQUIRE(queue_destroy(&queue) == 0);
            cleaned();
            return;
        }
    }
    REQUIRE(0); /* Evita um harness que não conclui por implementação anômala. */
}

static void selftest(void) {
    /* Valida os wrappers com primitivas isoladas; não implementa uma fila. */
    pthread_mutex_t lock;
    pthread_cond_t first, second;
    reset(2, ENOMEM);
    REQUIRE(__wrap_pthread_cond_init(&first, NULL) == 0);
    REQUIRE(__wrap_pthread_mutex_init(&lock, NULL) == ENOMEM);
    REQUIRE(__wrap_pthread_cond_destroy(&first) == 0);
    REQUIRE(injected && attempts == 2);
    cleaned();
    reset(3, EAGAIN);
    REQUIRE(__wrap_pthread_mutex_init(&lock, NULL) == 0);
    REQUIRE(__wrap_pthread_cond_init(&first, NULL) == 0);
    REQUIRE(__wrap_pthread_cond_init(&second, NULL) == EAGAIN);
    REQUIRE(__wrap_pthread_mutex_destroy(&lock) == 0);
    REQUIRE(__wrap_pthread_cond_destroy(&first) == 0);
    REQUIRE(injected && attempts == 3);
    cleaned();
}
int main(int argc, char **argv) {
    if (argc == 2 && !strcmp(argv[1], "selftest")) selftest();
    else if (argc == 2 && !strcmp(argv[1], "selftest-failed-destroy")) {
        pthread_mutex_t lock;
        reset(1, EAGAIN);
        REQUIRE(__wrap_pthread_mutex_init(&lock, NULL) == EAGAIN);
        __wrap_pthread_mutex_destroy(&lock); /* O wrapper deve rejeitar antes de pthread. */
    } else if (argc == 2 && !strcmp(argv[1], "selftest-leak")) {
        pthread_cond_t cond;
        reset(2, ENOMEM);
        REQUIRE(__wrap_pthread_cond_init(&cond, NULL) == 0);
        cleaned(); /* Deve rejeitar uma primitiva que não foi destruída. */
    }
    else if (argc == 1) { queue_trials(EAGAIN); queue_trials(ENOMEM); }
    else return 2;
    puts("PASS");
    return 0;
}
