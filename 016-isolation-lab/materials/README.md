# Como usar os materiais

Execute os comandos a partir da raiz deste pacote, que contém `materials/` e `checks/`.
Instale na VM Linux um compilador C11, Make e Python 3; os checks usam somente a
biblioteca padrão. Leia [contract.md](contract.md) antes de alterar o starter.

| Arquivo | Função |
| --- | --- |
| [supervisor.c](supervisor.c) | TODO central; retorna 125 sem criar filhos |
| [vm_guard.h](vm_guard.h) | Confirmação humana exigida antes de execução |
| [probe.c](probe.c) | Alvos benignos; no máximo um filho e uma reserva virtual de 128 MiB |
| [Makefile](Makefile) | Compila sem executar nenhum alvo |
| [check.py](../checks/check.py) e [vm.py](../checks/vm.py) | Contrato público e guarda dos scripts |
| [experiências](../experiments/README.md) | Investigação de recursos e isolamento |

## Compilação permitida no host

```sh
make -C materials
make -C materials static-check
```

Os binários ficam em `materials/build/` e não entram no pacote. Para outro destino,
use `make -C materials BUILD=/tmp/oxide-isolation-build`. Os checks esperam o destino
padrão dentro da VM. Não há dependências locais fora do pacote. Não use sanitizers
com os checks de RLIMIT_AS: eles alteram as reservas virtuais do processo.
A fixture `probe` usa `-fno-builtin-malloc`: Clang em `-O2` pode eliminar a
allocation que o experimento precisa observar. A flag não altera o supervisor.

## Execução exclusivamente dentro da VM descartável

Confirme a VM pelo console do hypervisor e registre imagem/snapshot, isolamento de
pastas e ausência de credenciais. A confirmação abaixo não faz essa verificação.
Use usuário sem privilégios; o teste de arquivo inacessível depende disso.

```sh
export OXIDE_DISPOSABLE_VM=confirmed
materials/build/probe ok
materials/build/probe sleep
materials/build/probe exit7
```

Resultados esperados: 0, aproximadamente dois segundos e status 0, depois status 7.
Capture `$?` imediatamente depois de cada comando no seu relatório. A fixture usa
`alarm(5)` como proteção adicional; isso não prova que o supervisor impôs prazo.
Não execute `child` ou `orphan` diretamente: use os checks, que detectam e executam reaping dos
processos deixados por uma implementação incorreta.

Implemente o contrato e execute:

```sh
make -C materials
python3 checks/check.py --confirm-disposable-vm
python3 experiments/observe.py --confirm-disposable-vm
```

O starter deve falhar no primeiro check funcional: ele retorna 125 em vez de 0.
Esse resultado esperado ainda precisa ser observado na VM. O check não compila uma
solução nem implementa o supervisor por você. A guarda também é testada, dentro da VM.

## Cobertura e recuperação

Antes de iniciar a bateria, os checks exigem hard AS herdado de pelo menos 64 MiB e
hard CPU de pelo menos 1 segundo, aceitando também RLIM_INFINITY. Sob essas condições,
`probe limits` compara soft e hard por igualdade com AS de 64 MiB, CPU de 1 segundo
e CORE zero. O contrato permite elevar o soft herdado até `min(teto, hard herdado)`
no filho; o pai conserva seus limites. Hard menor exige um teste separado na VM e
não é coberto pela bateria padrão.

Os checks verificam saída 0/7, término por SIGTERM, argumentos literais, limites,
allocation recusada, prazo, descendente que ignora SIGTERM, órfão, CLI inválida, falhas
de exec, arquivo sem permissão e file descriptor que deve fechar antes de exec.
Cada invocação tem espera externa de oito segundos. O check adota sobras como subreaper,
sinaliza somente filhos próprios e executa reaping dessas sobras; qualquer sobra reprova o caso.
Nenhum PID fixo nem busca por nome é usada para matar processos.

Se a limpeza externa falhar, encerre e descarte a VM pelo hypervisor. Não continue
uma bateria com estado desconhecido. Os alvos dormem por no máximo dois segundos
e têm alarme de emergência de cinco segundos; não produzem carga ilimitada.
Os checks não cobrem todas as falhas de preparação, limites menores herdados ou
interrupção do supervisor por sinais. A revisão desses caminhos é obrigatória.

Sem VM, use [o percurso teórico](../experiments/theory.md). Nunca configure a guarda
no host para obter uma saída de teste. Registre no [relato](../report-template.md)
o que foi compilado e o que continua sem execução.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** Livre com acesso às APIs Linux; por exemplo C, Rust, Go e Python.

**Linguagens recomendadas:** Rust, Go e Python.

**Restrições técnicas e plataforma:** Linux em VM descartável, sem privilégios; manter todas as restrições do roteiro.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve CLI, prazos 100..5000 ms, limites, status e reaping inclusive de órfãos. Bibliotecas auxiliares de syscall são permitidas; supervisor ou sandbox prontos substituem o mecanismo e não são aceitos. Testes de runtime exigem VM: sucesso de compilação não comprova isolamento.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

Somente na VM preparada conforme o roteiro, use `python3 checks/check.py --confirm-disposable-vm --supervisor /caminho/supervisor`. O check preserva `OXIDE_DISPOSABLE_VM=confirmed`, usuário sem privilégios e as demais guardas. `--probe` seleciona o probe compilado. O diagnóstico continua exigindo o prefixo `supervisor:`.

## Observação inicial de processos próprios no host

Antes da etapa guardada, observe somente ferramentas prontas e benignas: execute
`sleep 1 &`, anote `$!` e use `wait "$!"` no mesmo shell para recolher esse filho.
Explique a diferença entre iniciar, esperar e obter o status. Isso atende à primeira
etapa de processos próprios; não executa o supervisor nem as fixtures deste pacote.
A compilação continua permitida no host. `probe`, supervisor, checks e experimentos
de isolamento mantêm todas as guardas e só executam na VM descartável.

A VM dos checks exige `PR_SET_CHILD_SUBREAPER` e procfs com
`CONFIG_PROC_CHILDREN` (`/proc/<pid>/task/<pid>/children`). As janelas de tempo foram verificadas em VM Alpine/QEMU em 25/10/2026.
Registre condições e carga; essa observação não garante latência universal.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
