/* SPDX-License-Identifier: MIT */
.data
.globl probe_count, probe_alignment
probe_count: .quad 0
probe_alignment: .quad 0
.text
.globl alignment_probe
.type alignment_probe,@function
alignment_probe:
    incq probe_count(%rip)
    mov %rsp,%rax
    and $15,%eax
    mov %rax,probe_alignment(%rip)
    /* Nenhum dado do chamador pode sobreviver aqui na red zone através de call. */
    mov $-1,%rax
    .irp offset,8,16,24,32,40,48,56,64,72,80,88,96,104,112,120,128
    mov %rax,-\offset(%rsp)
    .endr
    .irp reg,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    pxor %xmm\reg,%xmm\reg
    .endr
    /* Um chamado pode destruir registradores caller-saved. */
    mov $-1,%rax
    mov %rax,%rdi
    mov %rax,%rsi
    mov %rax,%rdx
    mov %rax,%rcx
    mov %rax,%r8
    mov %rax,%r9
    mov %rax,%r10
    mov %rax,%r11
    ret
.size alignment_probe,.-alignment_probe
.globl invoke_checked
.type invoke_checked,@function
invoke_checked:
    push %rbx
    push %rbp
    push %r12
    push %r13
    push %r14
    push %r15
    sub $24,%rsp
    mov %rsi,(%rsp)
    mov %rdi,%rax
    movabs $0x1234567800000065,%rbx
    movabs $0x2345678900000066,%rbp
    movabs $0x3456789a00000067,%r12
    movabs $0x456789ab00000068,%r13
    movabs $0x56789abc00000069,%r14
    movabs $0x6789abcd0000006a,%r15
    push 56(%rax)
    push 48(%rax)
    mov 0(%rax),%rdi
    mov 8(%rax),%rsi
    mov 16(%rax),%rdx
    mov 24(%rax),%rcx
    mov 32(%rax),%r8
    mov 40(%rax),%r9
    call arithmetic8
    /* Limpe DF antes de voltar ao C, mesmo quando o participante o deixou ligado. */
    pushfq
    pop %rdx
    cld
    test $0x400,%rdx
    setnz 32(%rsp)
    add $16,%rsp
    mov (%rsp),%rdx
    mov %rax,(%rdx)
    xor %eax,%eax
    cmpb $0,16(%rsp)
    jne 1f
    movabs $0x1234567800000065,%rdx
    cmp %rdx,%rbx
    jne 1f
    movabs $0x2345678900000066,%rdx
    cmp %rdx,%rbp
    jne 1f
    movabs $0x3456789a00000067,%rdx
    cmp %rdx,%r12
    jne 1f
    movabs $0x456789ab00000068,%rdx
    cmp %rdx,%r13
    jne 1f
    movabs $0x56789abc00000069,%rdx
    cmp %rdx,%r14
    jne 1f
    movabs $0x6789abcd0000006a,%rdx
    cmp %rdx,%r15
    jne 1f
    jmp 2f
1:  mov $1,%eax
2:  add $24,%rsp
    pop %r15
    pop %r14
    pop %r13
    pop %r12
    pop %rbp
    pop %rbx
    ret
.size invoke_checked,.-invoke_checked
.section .note.GNU-stack,"",@progbits
