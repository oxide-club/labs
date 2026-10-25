/* SPDX-License-Identifier: MIT */
#ifndef LAB_NO_MAIN
#include <errno.h>
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
    int fd = 1;
    if (argc == 2 && strcmp(argv[1], "--bad-fd") == 0) fd = -1;
    else if (argc != 1) return 2;
    if (write_all(fd, "oxide\n", 6) == 0) return 0;
    fputs(errno == EBADF ? "EBADF\n" : "write failed\n", stderr);
    return 1;
}
#endif
