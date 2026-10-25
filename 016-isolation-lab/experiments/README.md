# Investigar recursos e fronteiras

Faça a execução apenas na VM descartável confirmada no [guia](../materials/README.md).
Se a VM ou as permissões não estiverem disponíveis, siga [o percurso teórico](theory.md).
Nenhum comando deste pacote configura recursos do host. A investigação dos três
mecanismos é obrigatória; ativá-los depende de permissões verificadas dentro da VM.

## Prever, observar e explicar o núcleo

Antes dos checks, preencha a tabela com suas previsões. Depois, acrescente status,
duração observada e explicação. Não preencha observação com o resultado esperado.

| Alvo | Pergunta | Resultado esperado sob contrato |
| --- | --- | --- |
| `sleep`, prazo 300 ms | Dormir consome 300 ms de CPU? | Timeout 124 por tempo de parede |
| `alloc` | A reserva de 128 MiB cabe em 64 MiB de espaço virtual? | `allocation=denied`, status 0 |
| `limits` | Limites pertencem ao pai ou ao executado? | Status 0; confira também limites do pai |
| `child`, prazo 300 ms | SIGTERM basta se o filho o ignora? | 124, sem processos restantes após SIGKILL/reaping |
| `orphan` | Quem executa reaping do filho depois que o principal sai? | 7 após limpar e executar reaping do descendente |
| `denied` | Um arquivo modo 000 é uma sandbox? | `file=denied`; apenas este acesso foi recusado |
| `fd` | O exec fecha automaticamente todo file descriptor? | O supervisor precisa fechar o file descriptor herdado |

O check cria o arquivo sem permissão em seu diretório temporário, restaura a permissão
e remove o diretório. Não substitua esse caminho por arquivo do sistema ou do host.
Para investigar sinais recebidos pelo supervisor, crie um teste na VM que espere a
confirmação de preparação, envie SIGTERM ao PID próprio do supervisor e verifique 143
e ausência de filhos. Não use uma espera fixa como prova de que a preparação terminou.

## Inventário inicial sem mudanças de configuração

```sh
python3 experiments/observe.py --confirm-disposable-vm
```

Registre IDs de namespaces, associação a cgroup, controllers visíveis e campos
Seccomp/NoNewPrivs/CapEff. Um controller visível não significa que o usuário pode
delegá-lo. Seccomp diferente de zero não revela quais syscalls a política permite.
Um namespace de cgroup muda a visão da hierarquia; não concede memória adicional.

## Comparação obrigatória

Preencha as colunas de evidência e restrição usando as [fontes primárias](../references.md).
Se um teste exigir privilégios não disponíveis, registre a restrição e complete a
análise teórica; não altere sysctls nem a hierarquia global para forçar a execução.

| Mecanismo | O que investigar | Permissão ou condição | Evidência a produzir |
| --- | --- | --- | --- |
| Limites por processo | RLIMIT_AS, CPU e CORE no filho | Redução dos próprios limites; hard herdado suficiente | Status e leitura de getrlimit; diferença entre virtual/RSS/CPU/parede |
| Namespaces | Visões de PID, usuário e mount | Suporte do kernel e política de user namespaces; capabilities variam por tipo | Compare `/proc/self/ns/*`, UID interno/externo e visibilidade de processos antes/depois de um experimento próprio |
| cgroup v2 | Contabilização agregada e tetos | Subárvore delegada exclusivamente para o laboratório, controllers habilitados | Plano de `memory.max`, `pids.max`, `cpu.max`; leituras `memory.current`, `memory.events`, `pids.current` |
| seccomp | Filtragem de syscalls do próprio processo | Filtros habilitados; no_new_privs ou capability apropriada | Política, arquitetura, syscall benigna escolhida, ação e errno/sinal observado ou previsto |

Para um experimento de namespaces, planeje primeiro criação, erros possíveis,
retorno ao processo chamador e descarte do ambiente. Compare visibilidade, sem concluir
que namespaces limitam consumo ou eliminam vulnerabilidades do kernel compartilhado.
Não use mounts sobre diretórios compartilhados com o host.

Para cgroups, escreva um plano restrito à subárvore delegada: crie um grupo vazio,
estabeleça limites antes de colocar o alvo benigno, observe contadores e execute reaping dos
processos antes de remover o grupo. Use memória e número de processos pequenos.
Não execute esse plano sem comprovar a delegação; não mova o shell ou serviços do sistema.
O núcleo usa rlimits; ele não implementa automaticamente esse plano.

Para seccomp, desenhe uma política que recuse uma syscall benigna e mantenha as
operações necessárias a diagnóstico e saída. Valide a arquitetura dos números de
syscall e explique a ordem de no_new_privs, filtro e exec. Não aplique a política ao
shell. `SECCOMP_MODE_STRICT` pode encerrar um programa C que usa operações da libc
fora de seu conjunto permitido; uma lista ingênua de syscalls não é uma sandbox.

## Evidência e limites

Para cada mecanismo, entregue uma previsão, observação quando disponível, regra da
documentação, permissão exigida e um contraexemplo à garantia excessiva. Explique
file descriptors abertos antes do isolamento, acesso ao filesystem, capabilities e rede.
Distinga falha de permissão do ambiente de defeito na implementação. Um programa
benigno que passa não demonstra contenção de um programa adversarial.
