# Referências orientadas — Evidências de hardening em executáveis ELF

1. [GCC — Instrumentation Options](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html): comparar `-fstack-protector`, `-strong` e `-all`; identificar como a otimização afeta objetos considerados.
2. [GNU ld — Options](https://sourceware.org/binutils/docs/ld/Options.html): localizar `pie`, `noexecstack`, `relro` e `now`; relacionar cada opção à evidência coletada.
3. [Linux Kernel — `randomize_va_space`](https://docs.kernel.org/admin-guide/sysctl/kernel.html#randomize-va-space): interpretar a política sem modificá-la e distinguir regiões afetadas.
4. [glibc — `elf/dl-reloc.c`](https://raw.githubusercontent.com/bminor/glibc/glibc-2.42/elf/dl-reloc.c): código de produção; ler `_dl_relocate_object` e `_dl_protect_relro`, localizando a chamada que aplica leitura após relocations. Registrar a revisão consultada.

## Situação das referências

Consulta em 25/10/2026: manuais GCC, GNU ld e kernel acessíveis. O código glibc foi consultado na release `glibc-2.42`; a URL tentada para `glibc-2.44` retornou 404. A versão lida é uma referência de produção, não uma identificação do fonte da glibc 2.44 instalada. Os manuais permanecem móveis; registre as versões efetivamente usadas no experimento.

No código de produção, examine `_dl_relocate_object` e `_dl_protect_relro`. A segunda função alinha o intervalo por páginas e pede `PROT_READ` por `__mprotect`. O loader trata relocations e compatibilidade de muitos objetos; a sonda apenas observa seu próprio processo. Pergunta: por que o loader precisa terminar as relocations antes de retirar a permissão de escrita?

A implementação real pode ter requisitos de portabilidade, desempenho e compatibilidade além do experimento. Use a pergunta de leitura para explicar essa diferença; não copie o código como solução didática. As leituras exigidas no roteiro continuam parte da investigação.
