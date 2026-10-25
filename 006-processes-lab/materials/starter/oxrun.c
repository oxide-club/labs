/* SPDX-License-Identifier: MIT */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>

int main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    /* TODO: validar argv antes de criar filhos; implementar run e pipe.
       Usar fork/execvp/waitpid e pipe/dup2/close diretamente.
       Retomar waitpid após EINTR; recuperar preparação parcial. */
    fputs("oxrun: implementação pendente\n", stderr);
    return 2;
}
