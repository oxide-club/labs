# Referências orientadas

Consulta em 25/10/2026. Leituras externas complementam o pacote; não são dependências de execução.

- [write(2)](https://man7.org/linux/man-pages/man2/write.2.html), consultado: retornos parciais, EINTR e EBADF. Explique quando o chamador deve repetir.
- [syscall(2)](https://man7.org/linux/man-pages/man2/syscall.2.html), consultado: função da libc, errno e tabela de registradores. Compare função C e ABI Linux x86-64.
- [Linux v6.12, fs/read_write.c](https://github.com/torvalds/linux/blob/v6.12/fs/read_write.c), arquivo consultado: procure `SYSCALL_DEFINE3(write`, `ksys_write` e `vfs_write`. Localize validação e encaminhamento ao arquivo. Revisão fixada por tag de release; não é o kernel do ambiente necessariamente.
- [musl v1.2.5, src/unistd/read.c](https://github.com/ifduyue/musl/blob/v1.2.5/src/unistd/read.c): leitura curricular para localizar a camada de wrapper e o caminho syscall de cancelamento. Acesso web falhou com cache miss durante preparação; mecanismo e revisão não foram confirmados nesta consulta. Não inferir que o ambiente usa musl.

Aprofundamento: Zhirkov, Low-Level Programming, capítulo 6 e apêndice C; não é necessário possuir o livro para executar este pacote.
