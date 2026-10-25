/* SPDX-License-Identifier: MIT */
#include "arithmetic.h"
#include <inttypes.h>
#include <stdio.h>
int main(void) {
    uint64_t a[8], expected, result = 0;
    int failed = 0;
    while (scanf("%" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64,
           &a[0],&a[1],&a[2],&a[3],&a[4],&a[5],&a[6],&a[7],&expected)==9) {
        probe_count=0; probe_alignment=0;
        uint64_t damaged=invoke_checked(a,&result);
        uint64_t reference=call8(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7]);
        if (result!=expected || reference!=expected || damaged || probe_count!=1 || probe_alignment!=8) {
            fprintf(stderr,"Falha: resultado=%" PRIu64 " esperado=%" PRIu64 " preservacao=%" PRIu64 " chamadas=%" PRIu64 " alinhamento=%" PRIu64 "\n",result,expected,damaged,probe_count,probe_alignment);
            failed=1;
        }
    }
    return failed;
}
