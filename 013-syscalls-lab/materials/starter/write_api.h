/* SPDX-License-Identifier: MIT */
#ifndef WRITE_API_H
#define WRITE_API_H
#include <stddef.h>
int write_all(int fd, const void *buf, size_t length);
#endif
