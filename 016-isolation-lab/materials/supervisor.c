/* SPDX-License-Identifier: MIT */
#include "vm_guard.h"

int main(int argc, char **argv)
{
    if (!vm_confirmed()) return 125;
    (void)argc;
    (void)argv;
    /* TODO: implemente contract.md. Preserve a guarda antes de qualquer fork.
     * Valide CLI; prepare subreaper, sincronização e grupo exclusivo.
     * Aplique limites e feche file descriptors no filho; execute argv sem shell.
     * Distinga erro de preparação/exec de saída normal.
     * Espere com prazo monotônico; encerre toda a árvore própria e execute reaping dos processos.
     * Garanta limpeza também após falhas parciais e sinais recebidos.
     */
    fputs("supervisor: TODO de supervisão não implementado\n", stderr);
    return 125;
}
