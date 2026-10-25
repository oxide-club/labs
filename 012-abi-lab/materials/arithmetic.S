/* SPDX-License-Identifier: MIT */
.text
.globl arithmetic8
.type arithmetic8,@function
arithmetic8:
    /* TODO: preservar estado, chamar alignment_probe e calcular o contrato. */
    xor %eax, %eax
    ret
.size arithmetic8, .-arithmetic8
.section .note.GNU-stack,"",@progbits
