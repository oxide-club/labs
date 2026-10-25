/* SPDX-License-Identifier: MIT */
#include "write_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <stdarg.h>
#include <string.h>
#include <sys/syscall.h>
#include <sys/types.h>
static const char data[] = "abcdef";
static int mode, calls;
static int libc_calls, syscall_calls;
static size_t accepted;
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL modo=%d chamadas=%d linha=%d: %s\n", mode, calls, __LINE__, #x); exit(1); } } while (0)
static ssize_t scripted(int fd, const void *buf, size_t n) {
    CHECK(fd == 17 && calls++ < 8);
    CHECK(buf == data + accepted);
    CHECK(n == 6 - accepted && memcmp(buf, data + accepted, n) == 0);
    if ((mode == 1 && calls == 1) || (mode == 5 && calls == 2)) { errno = EINTR; return -1; }
    if (mode == 2 || (mode == 3 && calls == 2)) { errno = EBADF; return -1; }
    if (mode == 4) return 0;
    size_t take = n > 2 ? 2 : n;
    accepted += take;
    return (ssize_t)take;
}
ssize_t __wrap_write(int fd, const void *buf, size_t n) { ++libc_calls; return scripted(fd, buf, n); }
long __wrap_syscall(long number, ...) {
    CHECK(number == SYS_write);
    va_list ap; va_start(ap, number);
    int fd = va_arg(ap, int);
    const void *buf = va_arg(ap, const void *);
    size_t n = va_arg(ap, size_t); va_end(ap);
    ++syscall_calls;
    return scripted(fd, buf, n);
}
int main(void) {
    CHECK(write_all(17, NULL, 0) == 0 && calls == 0);
    for (mode = 0; mode <= 5; mode++) {
        calls = 0; accepted = 0; errno = EINTR;
        int r = write_all(17, data, 6);
        if (mode < 2) CHECK(r == 0 && accepted == 6 && calls == 3 + mode);
        else if (mode < 4) CHECK(r == -1 && errno == EBADF && accepted == (mode == 3 ? 2 : 0) && calls == (mode == 3 ? 2 : 1));
        else if (mode == 4) CHECK(r == -1 && errno == EIO && calls == 1);
        else CHECK(r == 0 && accepted == 6 && calls == 4);
    }
#ifdef EXPECT_SYSCALL
    CHECK(syscall_calls > 0 && libc_calls == 0);
#elif defined(EXPECT_LIBC)
    CHECK(libc_calls > 0 && syscall_calls == 0);
#else
#error "Defina o backend esperado"
#endif
}
