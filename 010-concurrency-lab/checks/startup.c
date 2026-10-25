/* SPDX-License-Identifier: MIT */
#include "counter.h"
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>

int __real_pthread_create(pthread_t *, const pthread_attr_t *, void *(*)(void *), void *);
int __real_pthread_join(pthread_t, void **);
int __real_pthread_mutex_init(pthread_mutex_t *, const pthread_mutexattr_t *);
int __real_pthread_mutex_destroy(pthread_mutex_t *);
static unsigned created, joined, destroyed, fail_after;
static int fail_init;
int __wrap_pthread_create(pthread_t *thread, const pthread_attr_t *attr,
                          void *(*fn)(void *), void *arg) {
    if (created == fail_after) return EAGAIN;
    int code = __real_pthread_create(thread, attr, fn, arg);
    if (!code) ++created;
    return code;
}
int __wrap_pthread_join(pthread_t thread, void **result) {
    int code = __real_pthread_join(thread, result);
    if (!code) ++joined;
    return code;
}
int __wrap_pthread_mutex_init(pthread_mutex_t *lock, const pthread_mutexattr_t *attr) {
    return fail_init ? EAGAIN : __real_pthread_mutex_init(lock, attr);
}
int __wrap_pthread_mutex_destroy(pthread_mutex_t *lock) {
    int code = __real_pthread_mutex_destroy(lock);
    if (!code) ++destroyed;
    return code;
}
int main(void) {
    uint64_t out = 123;
    fail_init = 1;
    assert(counter_run(COUNTER_MUTEX, 4, 10, &out) == EAGAIN);
    assert(out == 123 && created == 0 && joined == 0 && destroyed == 0);
    fail_init = 0;
    for (fail_after = 0; fail_after < 4; ++fail_after) {
        created = joined = destroyed = 0;
        assert(counter_run(COUNTER_MUTEX, 4, 10, &out) == EAGAIN);
        assert(out == 123 && created == fail_after && joined == created && destroyed == 1);
    }
    puts("PASS");
    return 0;
}
