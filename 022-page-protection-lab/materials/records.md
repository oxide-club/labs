# Registros e refinamento operacional — revisão 2

Este formato fecha as interfaces auxiliares do enunciado. Use JSONL em stdout: um objeto por caso. Diagnósticos vão para stderr. Não grave cabeçalhos em stdout.

## Seleção e ordem

`--case all|<id>` seleciona os casos; a omissão equivale a `all`. `--timeout-ms N` aceita inteiros de 100 a 10000, padrão 2000. Rejeite opções desconhecidas, repetidas, incompletas e números inválidos com saída 2, antes de criar filhos e sem registros de sondas.

A ordem de `all` é: `none-read`, `none-write`, `r-read`, `r-write`, `w-read`, `w-write`, `rw-read`, `rw-write`, `transition`, `unaligned`, `zero-length`, `hang`, `continuity`. A última leitura RW deve executar depois do timeout. Cada seleção individual também deve funcionar.

## Campos obrigatórios

| Campo | Conteúdo |
| --- | --- |
| `id` | ID acima |
| `protection` | `NONE`, `R`, `W`, `RW`; `RW-R-RW` para transição; `R` para unaligned |
| `permissions` | Quatro caracteres de `/proc/self/maps` para a página central; `----` se indisponível por erro anterior |
| `operation` | `read`, `write`, `transition`, `setup` ou `wait` |
| `duration_ms` | Número finito não negativo, relógio monotônico desde a criação até o child reaping |
| `result` | `ok`, `signal`, `setup_error`, `timeout` ou `unsupported` |
| `exit_code` | Código real do filho; -1 se terminou por sinal |
| `signal` | Número real do sinal obtido de waitpid; 0 se saiu normalmente |
| `errno` | Número do erro de preparação; 0 quando ausente |
| `byte` | Byte lido/verificado em decimal; -1 quando a operação não terminou |
| `detail` | Texto diagnóstico; na transição bem-sucedida, `165,165,90` |
| `pid` | PID do filho, sem valor fixo esperado |
| `reaped` | Booleano: status coletado antes de emitir o registro |
| `page_size`, `pages` | Tamanho consultado e quantidade 3 |

A transição lê `0xA5` sob RW, muda para R e lê `0xA5`, restaura RW, escreve `0x5A` e verifica o byte. Registre as permissões de cada etapa no trace suplementar; `permissions` contém a última observação. No caso de escrita sob W, não imponha leitura adicional enquanto a página estiver somente W: confira após restaurar leitura, se necessário. Nas sondas proibidas use a sonda assembly, nunca uma expressão C inválida.

## Resultados e códigos

As três sondas proibidas exigem status real `WIFSIGNALED` e `SIGSEGV` (11 no alvo). Uma saída normal 11 ou 139 não serve. O byte inicial é 165; o byte escrito é 90. `w-read` é observacional: aceita sucesso/165 ou SIGSEGV.

`unaligned` deve observar a syscall Linux `mprotect` retornando -1/EINVAL. Na VM com musl, use `syscall(SYS_mprotect, ...)` nesse controle: o wrapper da libc ajusta o endereço, como descrito em [vm.md](vm.md). `zero-length` deve observar `mmap` retornando MAP_FAILED/EINVAL. Os filhos desses dois casos saem com 2 e não executam a sonda depois do erro. Ambos registram `setup_error`, errno 22, sinal 0, byte -1.

**Refinamento operacional aprovado pelo responsável em 25/10/2026 nesta conversa de preparação:** `all` retorna 0 quando os erros INTENCIONAIS e o timeout esperado foram conferidos, os resultados obrigatórios coincidem e o caso observacional foi classificado. Isso também vale para a seleção individual desses controles. Erro inesperado de preparação ou `unsupported` retorna 2; divergência retorna 1. Na agregação, 2 tem precedência sobre 1, que tem precedência sobre 0. Não converta falhas imprevistas em controles aprovados.

Para `hang`, o filho aguarda sem acessar memória. O supervisor usa SIGKILL, coleta o status e registra `timeout`, sinal 9, saída -1. A tolerância operacional dos checks é N até N+1500 ms. Essa tolerância mede o funcionamento do prazo neste runner; não é uma promessa universal de latência. Sob carga que exceda o limite, registre a limitação e repita em runner disponível. O próximo caso precisa concluir normalmente.

Se `/proc` ou outra preparação obrigatória falhar, use `setup_error`. Se a arquitetura não for suportada ou o mapeamento receber `x` implicitamente, use `unsupported`, saída agregada 2, e não execute a sonda. Não altere a política global. Os checks reportam ambiente incompatível separadamente; isso não aprova o núcleo.

## Auditoria complementar

O check confere o comportamento declarado e executa `checks/audit_trace.py` para confrontá-lo com um trace independente. A auditoria exige terminação real por SIGSEGV/SIGKILL ou saída normal 0/2, conforme o caso, e o status correspondente de wait4. A entrega de um sinal não equivale à terminação por ele. Saída 139 não equivale a SIGSEGV. Revise o código e preserve traces de mmap/mprotect/munmap, waitpid, kill e close, além dos mapeamentos. Confira uma região nova por filho, apenas a página central sondada, ausência de acesso após erro, encerramento de descritores e ausência de filhos pendentes. Os endereços são observações, nunca fixtures.

A auditoria retorna 2 se strace ou ptrace estiver indisponível; esse estado não aprova o laboratório. O check rejeita processos que permaneçam no grupo após a saída do supervisor. Um processo que escape do grupo exige revisão adicional; não se afirma detecção universal de vazamentos.


### Alcance da auditoria de espera

A auditoria fornecida reconhece somente a syscall `wait4`, usada por `waitpid` no Linux validado.
Ela não interpreta `waitid`. Um supervisor que use essa alternativa exige adaptação e validação do auditor;
a rejeição por status ausente, nesse caso, não prova que o supervisor relatou um sinal incorreto.
Esta é uma limitação do instrumento fornecido, não uma equivalência entre as duas APIs.
