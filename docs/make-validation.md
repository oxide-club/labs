# Validação dos demais Makefiles — 25/10/2026

Os 15 laboratórios fora da integração QEMU foram exportados pela função real
`labFiles` do website para `/tmp/oxide remaining packages`, sem arquivos do
repositório pai. Foram executados 133 comandos: help, setup, build, test,
verify-preparation, run e clean em 19 combinações de referência/variante.
O laboratório 017 usou MODE=cpu nessa matriz.

Todos os comandos help, setup, build, verify-preparation e clean dessa matriz
retornaram zero. Falhas de starters em test/run foram mantidas; nenhum starter
foi implementado para fazer os checks passarem.

| Lab | Variante | test | run |
| --- | --- | --- | --- |
| 001 | reference | 2 | 0 |
| 004 | reference | 2 | 0 |
| 005 | reference | 2 | 2 |
| 005 | rust | 2 | 2 |
| 006 | reference | 2 | 2 |
| 007 | reference | 0 | 2 |
| 008 | reference | 2 | 2 |
| 009 | reference | 2 | 2 |
| 009 | rust | 2 | 2 |
| 010 | reference | 2 | 0 |
| 010 | rust | 2 | 0 |
| 011 | reference | 2 | 2 |
| 011 | go | 2 | 0 |
| 012 | reference | 2 | 0 |
| 013 | reference | 2 | 2 |
| 014 | reference | 2 | 2 |
| 015 | reference | 2 | 2 |
| 017 | reference / cpu | 0 | 0 |
| 018 | reference | 2 | 0 |

Os números são os status do GNU Make no host (0: sucesso; 2: erro). Em 007 e
013, run retornou 2 no sandbox por bloqueio de ptrace; repetido com permissão
para strace, ambos retornaram 0. As evidências parciais do erro foram preservadas.
Os demais erros correspondem aos starters incompletos.

Adicionalmente, `make run EXPERIMENT=model` no 010 passou;
`make run EXPERIMENT=measure` no 018 recusou a medição após falhar nos checks,
como previsto para o starter original.

## Recursos GPU

A investigação inicial ocorreu dentro do sandbox, que ocultava os dispositivos
`/dev/nvidia*`. A indisponibilidade observada era restrita a esse ambiente, não
à máquina: fora do sandbox, NVIDIA-SMI reconheceu a RTX 4060 e o driver 615.78.08.
A correção de setup continua válida: detecta quando as ferramentas existem, mas
o dispositivo não está acessível. Os testes cobrem ambas as condições.

A pedido do responsável, a interface Make foi exercitada fora do sandbox,
com acesso à RTX 4060 (runtime e driver CUDA reportados: 13040):

| Comando | Status do Make | Resultado |
| --- | --- | --- |
| `make setup MODE=gpu` | 0 | Sonda verificou dispositivo, alocação e cópias |
| `make build MODE=gpu` | 0 | Binários CUDA compilados e atualizados |
| `make test MODE=gpu` | 2 | Primeiro caso, n=0/bloco=64, recusado com operation not supported |
| `make run MODE=gpu` | 2 | Medição recusada porque os checks falharam |

O arquivo distribuído `materials/kernels.cu` ainda contém os TODOs de
`launch_add` e `launch_reduce`, ambos retornando `cudaErrorNotSupported`.
Seu SHA256, igual no checkout principal, no branch e no pacote testado, é
`86abce55506290ee1b9bc9df9126735630960993c1a3f50fa1d6c99200656f56`.
A suíte para na primeira falha: os demais casos não foram aprovados nem medidos.
Não há implementação de kernels nesse starter que possa ser declarada validada.
Os fontes foram preservados; não foi introduzida uma solução do exercício.

[Logs de setup, build, test e run](evidence/2026-10-25-make-gpu/results.json)
registram esta execução. O README da atividade menciona uma implementação
privada validada anteriormente; isso não torna o starter distribuído completo.

## Evidências

[Matriz de comandos e status](evidence/2026-10-25-make-remaining/results.json).
Logs adicionais em [evidências desta validação](evidence/2026-10-25-make-remaining/).
A validação QEMU dos outros três laboratórios está em
[Alpine com Clang](alpine-clang-validation.md).

Verificação final: 46 testes Python passaram; gerador Make, templates de relatórios
e modelo de cache sem divergências; 18 laboratórios sem erros estruturais.
Revisão independente da continuação concluída sem achados materiais.
