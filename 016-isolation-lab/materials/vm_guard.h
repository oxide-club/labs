/* SPDX-License-Identifier: MIT */
#ifndef OXIDE_VM_GUARD_H
#define OXIDE_VM_GUARD_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Confirmação humana, não detecção de VM nem barreira de segurança. */
static int vm_confirmed(void)
{
    const char *value = getenv("OXIDE_DISPOSABLE_VM");
    if (value && strcmp(value, "confirmed") == 0) return 1;
    fputs("supervisor: execução exige VM descartável e OXIDE_DISPOSABLE_VM=confirmed\n", stderr);
    return 0;
}
#endif
