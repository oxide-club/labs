# Auditoria da sonda x86-64

Origem: código original Oxide Club, 25/10/2026, MIT. ABI System V AMD64. O argumento chega em RDI; leitura devolve o byte zero-extended em EAX. A escrita modifica somente o byte apontado e não devolve valor. Não há syscalls, loops, tratamento de sinais, alocação ou código gerado. `ret` usa a stack normal da chamada. A seção `.note.GNU-stack` não solicita stack executável.

Compile com `make -C materials/starter/c audit`. Inspecione também o binário final com `objdump -d materials/starter/c/pageprobe`. No starter as funções estão presentes, mas ainda não são chamadas.

Disassembly observado com GCC 16.2.1 e GNU Binutils 2.47:

```asm
<probe_read>:
  movzbl (%rdi),%eax
  ret
<probe_write>:
  movb $0x5a,(%rdi)
  ret
```

Confira acesso de um byte e preservação dos registradores callee-saved. Endereços e bytes do disassembly não são critérios rígidos. A revisão é local: duas funções mínimas, sem instruções de execução de dados nem PROT_EXEC. O supervisor deve decidir endereço, permissões, processo e prazo. Uma falha mata o filho; a sonda não tenta recuperá-lo com um handler.

Isso não torna definido em C ou Rust o acesso inválido. O experimento observa uma instrução nativa no ambiente declarado. A publicação ainda depende de revisão independente e piloto.
