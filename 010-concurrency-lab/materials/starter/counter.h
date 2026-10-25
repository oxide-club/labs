/* SPDX-License-Identifier: MIT */
#ifndef COUNTER_H
#define COUNTER_H
#include <stdint.h>
typedef enum { COUNTER_UNSAFE, COUNTER_MUTEX, COUNTER_ATOMIC } CounterMode;
int counter_run(CounterMode mode, unsigned threads, unsigned iterations, uint64_t *out);
#endif
