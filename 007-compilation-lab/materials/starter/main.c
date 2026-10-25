/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>
#include "operations.h"
#define INPUT_VALUE 5
int main(int argc, char **argv)
{
    int wait_mode = argc == 2 && strcmp(argv[1], "--wait") == 0;
    if (argc != 1 && !wait_mode) {
        if (fputs("Uso: program [--wait]\n", stderr) == EOF ||
            fflush(stderr) == EOF) return 1;
        return 2;
    }
    if (printf("%s result=%d\n", "oxide", add_global(INPUT_VALUE)) < 0 ||
        fflush(stdout) == EOF) return 1;
    if (wait_mode && getchar() == EOF && ferror(stdin)) return 1;
    return 0;
}
