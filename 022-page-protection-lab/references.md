# Referências orientadas — Page protection e access violations

1. [Linux man-pages — `mmap(2)`](https://man7.org/linux/man-pages/man2/mmap.2.html): ler proteções, flags, retornos e erros antes de escrever o gerenciador da região.
2. [Linux man-pages — `mprotect(2)`](https://man7.org/linux/man-pages/man2/mprotect.2.html): investigar alinhamento, `SIGSEGV` e implicações entre permissões dependentes da arquitetura.
3. [Linux man-pages — `waitpid(2)`](https://man7.org/linux/man-pages/man2/waitpid.2.html): localizar a classificação do status e explicar por que encerrar não dispensa realizar o child reaping.
4. [Linux — `mm/mprotect.c`](https://github.com/torvalds/linux/blob/v6.12/mm/mprotect.c): código de produção; começar em `do_mprotect_pkey` e localizar validação de alinhamento e tratamento de `READ_IMPLIES_EXEC`. Registrar a revisão consultada; não reimplementar o kernel.

## Situação das referências

Consulta em 25/10/2026: man-pages de `mprotect` e `waitpid`; código `mm/mprotect.c` da release Linux v6.12. Observe `do_mprotect_pkey`, alinhamento e `READ_IMPLIES_EXEC`. O kernel também trata políticas de segurança, contabilidade e concorrência, além deste experimento. Pergunta: por que conferir só as flags passadas pelo usuário não basta para concluir ausência de execução? A leitura de `mmap` permanece indicada; a revisão externa dessa página não foi registrada nesta rodada.

A implementação real pode ter requisitos de portabilidade, desempenho e compatibilidade além do experimento. Use a pergunta de leitura para explicar essa diferença; não copie o código como solução didática. As leituras exigidas no roteiro continuam parte da investigação.
