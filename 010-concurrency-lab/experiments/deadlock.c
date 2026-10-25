/* SPDX-License-Identifier: MIT */
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static pthread_mutex_t locks[2] = {PTHREAD_MUTEX_INITIALIZER, PTHREAD_MUTEX_INITIALIZER};
static pthread_barrier_t ready;
static void must(int code) { if (code) exit(2); }
static void *bad(void *arg) {
    unsigned first = *(unsigned *)arg;
    must(pthread_mutex_lock(&locks[first]));
    int code = pthread_barrier_wait(&ready);
    if (code != 0 && code != PTHREAD_BARRIER_SERIAL_THREAD) exit(2);
    must(pthread_mutex_lock(&locks[1 - first]));
    return NULL;
}
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    if (!strcmp(argv[1], "ordered")) {
        /* TODO: duas threads, ordem global dos locks, join, destroy. */
        fputs("TODO: ordered\n", stderr);
        return 77;
    }
    if (strcmp(argv[1], "bad")) return 2;
    must(pthread_barrier_init(&ready, NULL, 3));
    unsigned first[2] = {0, 1};
    pthread_t threads[2];
    for (unsigned i = 0; i < 2; ++i) {
        /* Falha encerra este processo e suas threads; supervisor executa seu reaping. */
        must(pthread_create(&threads[i], NULL, bad, &first[i]));
    }
    int code = pthread_barrier_wait(&ready);
    if (code != 0 && code != PTHREAD_BARRIER_SERIAL_THREAD) return 2;
    puts("both-first-locks-held");
    fflush(stdout);
    for (unsigned i = 0; i < 2; ++i) must(pthread_join(threads[i], NULL));
    return 1; /* Alcançar este ponto seria inesperado no modo bad. */
}
