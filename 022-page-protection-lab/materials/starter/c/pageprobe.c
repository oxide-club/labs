/* SPDX-License-Identifier: MIT — Oxide Club, 2026. */
#include <stdio.h>
#include "probe.h"
int main(int argc, char **argv) {
    (void)argc; (void)argv;
    /* TODO: validar todos os argumentos antes de fork.
     * TODO: região nova de três páginas por filho, inicialização 0xA5.
     * TODO: mprotect, /proc/self/maps sem x, sondas e transições.
     * TODO: controle desalinhado via syscall(SYS_mprotect) na VM musl.
     * TODO: canal de preparação, waitpid real, prazo monotônico,
     * kill + reap no timeout, fechar descritores em ambos os processos.
     * TODO: JSONL e decisão 0/1/2 conforme materials/records.md.
     */
    fputs("starter incompleto: implemente o supervisor\n", stderr);
    return 2;
}
