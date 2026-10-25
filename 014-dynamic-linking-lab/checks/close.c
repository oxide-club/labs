/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <stdlib.h>
int __real_dlclose(void *handle);
char *__real_dlerror(void);
static _Thread_local int injected_error;
char *__wrap_dlerror(void) {
    if (injected_error) {
        injected_error = 0;
        return "fixture: falha injetada de dlclose";
    }
    return __real_dlerror();
}
int __wrap_dlclose(void *handle) {
    fputs("fixture-close-call\n", stderr);
    if (getenv("OXIDE_TEST_CLOSE_FAIL")) {
        /* A falha substitui o erro anterior e dlerror o consome uma única vez. */
        (void)__real_dlerror();
        injected_error = 1;
        return -1;
    }
    return __real_dlclose(handle);
}
