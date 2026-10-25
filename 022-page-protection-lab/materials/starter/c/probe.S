/* SPDX-License-Identifier: MIT
 * Oxide Club, 2026. Linux x86-64, ABI System V.
 * Argumento em RDI; leitura devolve byte zero-extended em EAX.
 * Somente o supervisor decide quando e onde executar estas instruções.
 */
.text
.globl probe_read
.type probe_read,@function
probe_read:
    movzbl (%rdi), %eax
    ret
.size probe_read, .-probe_read
.globl probe_write
.type probe_write,@function
probe_write:
    movb $0x5a, (%rdi)
    ret
.size probe_write, .-probe_write
.section .note.GNU-stack,"",@progbits
