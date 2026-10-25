/* SPDX-License-Identifier: MIT */
#include "counter.h"
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    CounterMode mode;
    if (!strcmp(argv[1], "unsafe")) mode = COUNTER_UNSAFE;
    else if (!strcmp(argv[1], "mutex")) mode = COUNTER_MUTEX;
    else if (!strcmp(argv[1], "atomic")) mode = COUNTER_ATOMIC;
    else return 2;
    uint64_t out = 0;
    int error = counter_run(mode, 4, 100000, &out);
    if (error) { fprintf(stderr, "counter_run: %d\n", error); return 2; }
    printf("mode=%s threads=4 iterations=100000 observed=%" PRIu64 "\n", argv[1], out);
    return 0;
}
