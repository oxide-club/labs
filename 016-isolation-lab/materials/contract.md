# Contrato do supervisor

Ambiente: Linux em VM descartável, C11, libc e `/proc` disponível. Execute como usuário
sem privilégios. Compile no host se necessário, mas execute supervisor, fixtures,
checks dinâmicos e experiências **somente dentro da VM**. O núcleo não modifica cgroups,
namespaces, mounts, credenciais ou configuração do sistema. A solução didática **não é
adequada para execução de código adversarial em produção** sem arquitetura, revisão e
isolamento adicionais.

## Entrada e preparação

```text
supervisor TIMEOUT_MS -- EXECUTABLE [ARG ...]
```

`TIMEOUT_MS` contém somente dígitos ASCII, entre 100 e 5000, inclusive. Rejeite vazio,
sinais, espaços, sufixos e overflow. Aceite até 32 argumentos a partir de `EXECUTABLE`,
cada um com até 4096 bytes, sem contar NUL. `EXECUTABLE` não pode ser vazio. Preserve
argumentos vazios, espaços e metacaracteres; use `execv`, sem shell intermediário.
`EXECUTABLE` é um caminho absoluto ou relativo ao diretório atual; não busque em PATH.
O diretório atual e o ambiente são herdados. Não capture nem transforme stdout/stderr
do alvo. O supervisor não escreve em stdout.

Antes de interpretar a CLI, exija `OXIDE_DISPOSABLE_VM=confirmed`, como em `vm_guard.h`.
Essa declaração humana não detecta virtualização nem impõe isolamento. Não a configure
no host. Depois, valide toda a entrada antes de criar filhos. As ferramentas de
check também exigem a opção `--confirm-disposable-vm`.

## Processos sob responsabilidade

O supervisor cria um filho principal e um grupo de processos exclusivo desse filho.
O supervisor fica fora desse grupo. O alvo benigno pode criar **um** filho, não executa
`setsid`/`setpgid`, não troca credenciais e não cria mais descendentes. Esses são limites
do modelo, não entradas adversariais que o supervisor sabe conter. Não use fork bombs.

O supervisor deve tornar-se subreaper antes de criar o principal. No Linux, essa
propriedade permite que ele adote descendentes órfãos e execute reaping deles. Prepare o grupo antes
de liberar a execução do alvo; documente como a sincronização elimina a janela entre
`fork`, criação do grupo e um pedido de encerramento. Não envie sinais a PID/PGID zero,
ao grupo do chamador ou a processos que não pertençam à execução.

O término do principal inicia a limpeza dos descendentes mesmo se ele retornar 0.
Envie SIGTERM ao grupo próprio; depois de 100 ms, envie SIGKILL aos sobreviventes.
Execute reaping do principal e de todos os descendentes adotados com `waitpid`, tratando EINTR,
até ECHILD. Só então retorne. O status do principal permanece sendo o resultado,
mesmo se a limpeza dos descendentes exigir SIGKILL.

## Prazo e falhas

Conte tempo de parede com CLOCK_MONOTONIC desde imediatamente antes do primeiro fork.
Se ainda não tiver ocorrido reaping do principal quando o prazo vencer, o resultado é
timeout: encerre o grupo pela mesma sequência e execute reaping de todos os filhos. Ao observar
simultaneamente término e prazo, tente executar reaping do principal antes de declarar timeout.
Use espera blocking ou temporizada; não faça busy-loop.

Se receber SIGINT ou SIGTERM, o supervisor deve iniciar a limpeza e retornar 128+sinal.
Se a preparação falhar, inclusive após criar o filho, encerre todos os processos já
criados e execute reaping deles. Feche file descriptors e produza status 125. Antes da criação do grupo,
a limpeza pode precisar sinalizar diretamente o filho próprio. Não execute o alvo se
qualquer limite ou preparação falhar. Distinga falha de exec de saída normal por um
canal de erro com fechamento em exec, sem vazar esse canal ao programa executado.
Nunca deixe um filho esperando indefinidamente por uma confirmação de preparação.

## Limites aplicados apenas ao filho

Antes do exec, para cada recurso da tabela, leia o hard herdado e defina no filho
`soft = hard = min(teto, hard herdado)`. Trate RLIM_INFINITY como ausência de teto
herdado. Essa política permite elevar um soft herdado menor até o valor calculado,
sem elevar o hard herdado. O pai conserva ambos os seus limites. Não escolha valores
arbitrariamente menores que o resultado dessa regra.

Por exemplo, AS com soft de 32 MiB e hard ilimitado deve resultar em soft e hard de
64 MiB no filho. Se AS tiver soft de 16 MiB e hard de 32 MiB, ambos devem ficar em
32 MiB. O segundo ambiente é válido para o contrato, mas não para a bateria padrão.

| Recurso | Teto | O que limita |
| --- | --- | --- |
| RLIMIT_AS | 64 MiB (67108864 bytes) | Espaço de endereços virtual por processo; não mede RSS nem soma da árvore |
| RLIMIT_CPU | 1 segundo | CPU consumida por processo; não é tempo de parede |
| RLIMIT_CORE | 0 | Tamanho de core dumps sujeitos a esse limite |

Para a bateria padrão, o hard AS herdado deve ser pelo menos 64 MiB e o hard CPU,
pelo menos 1 segundo; RLIM_INFINITY também satisfaz essas condições. O check recusa
o ambiente antes de criar filhos se uma delas falhar. Nessas condições, `probe limits`
exige igualdade: AS soft/hard de 67108864 bytes, CPU soft/hard de 1 segundo e CORE
soft/hard de zero. Portanto, uma implementação que imponha AS de 32 MiB reprova.
Não há exigência de que o soft herdado já seja igual ao hard; vale a regra acima.
O ambiente deve permitir carregar as ferramentas e um executável C pequeno antes
dos ajustes. Registre incompatibilidades; não altere limites do host para contorná-las.
Não use ASan nesses checks: sua reserva virtual muda esse pressuposto. Feche no filho os file descriptors
acima de 2 antes do exec, exceto o canal de erro que fecha no exec. File descriptors 0, 1 e 2
continuam herdados; o núcleo não restringe filesystem, rede nem capabilities do usuário.
O número de processos é limitado pela fixture, não por RLIMIT_NPROC; esse último tem
semântica por usuário e não substitui um limite agregado do grupo.

## Status observável

| Condição | Status do supervisor |
| --- | --- |
| Principal sai normalmente | Mesmo status (0–255) |
| Principal termina por sinal S | 128+S, limitado ao formato de status do shell |
| Prazo excedido | 124 |
| Guarda ausente ou falha interna/de preparação | 125 |
| Exec falha com ENOENT | 127 |
| Exec falha com outro errno | 126 |
| CLI inválida, com guarda presente | 2 |
| Supervisor recebe SIGINT/SIGTERM | 128+sinal recebido |

Para erros do supervisor e timeout, escreva em stderr uma mensagem iniciada por
`supervisor:` que identifique a causa. Saídas normais podem coincidir com valores
reservados; registre a causa no relatório, sem inferi-la apenas do número. Não há
garantia geral de latência: a meta em VM sem sobrecarga é retornar até o prazo mais
1 segundo, incluindo limpeza. Kernel travado e processos em espera ininterruptível
estão fora do modelo; o prazo não resolve esses casos.

## Revisão obrigatória além dos checks

Explique as invariantes de grupo, adoção, fechamento de file descriptors e reaping.
Revise ou injete de forma controlada falhas de pipe/fork/setpgid/prctl/setrlimit/exec
na VM. Não provoque esgotamento global para simular falhas. Inclua o caso em que um
filho já existe quando a preparação falha. Os checks públicos não exercitam todos
esses caminhos; sua aprovação não demonstra uma fronteira de segurança.

## Destinos dos sinais e falha de fork

Nunca use `kill(-1, ...)`, `kill(0, ...)` ou um PID recebido sem validar seu valor.
Se `fork()` retornar `-1`, não existe filho criado por essa chamada: não envie sinal a
esse valor nem derive dele um grupo. Sinalize somente um PID positivo de filho próprio
ou `-pgid` depois de confirmar que `pgid > 1` identifica o grupo criado pelo supervisor.
O grupo do próprio supervisor e grupos alheios nunca são destinos. Revise esses caminhos
antes de qualquer execução em VM; um valor `-1` pode alcançar todos os processos permitidos.
