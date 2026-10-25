/* SPDX-License-Identifier: MIT */
#define _DEFAULT_SOURCE
#include "write_api.h"
#include <errno.h>
#include <sys/syscall.h>
#include <unistd.h>
int write_all(int fd, const void *buf, size_t length) {
    /* TODO: implementar o contrato usando syscall(SYS_write, ...). */
    (void)fd; (void)buf; (void)length;
    errno = ENOSYS;
    return -1;
}
#include "driver.h"
