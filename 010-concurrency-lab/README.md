# Concorrência e Sincronização

Leia [o enunciado e contrato](index.md). Execute os comandos neste diretório.
Dependências: Linux, compilador C11 com pthreads, linker GNU compatível com `--wrap` e Python 3.10+; sem pacotes Python externos.

```sh
python3 experiments/interleavings.py
python3 experiments/run.py
python3 checks/check.py
```

O primeiro comando verifica um modelo de duas threads com três etapas por incremento.
O segundo compila o contador defeituoso e o cenário de deadlock em diretório temporário.
O contador unsafe pode até exibir o produto esperado; isso não torna seu acesso válido no modelo C.
O processo de deadlock deve imprimir `both-first-locks-held`, atingir o timeout de 2 segundos configurado e ter seu reaping executado pelo script.
Esse prazo é um limite operacional, não uma medição de desempenho.
Não execute o binário de deadlock diretamente sem supervisor.

O terceiro comando compila os starters e executa casos independentes com timeout.
No starter, os checks de sincronização falham: o contador correto ainda não incrementa, a fila retorna ENOSYS e ordered retorna 77.
Com o starter distribuído, são esperadas 16 falhas de participante; counter-startup e deadlock bad passam.
Isso é trabalho previsto para o participante. Falha de compilação, dependência ausente ou importação quebrada são problemas de preparação distintos.
Os checks continuam após cada falha para mostrar os demais cenários.
O caso counter-startup injeta falhas na inicialização do mutex e na criação de threads; confere saída preservada, joins e destruição.
O caso queue-startup injeta EAGAIN e ENOMEM em cada tentativa de inicialização observada.
Ele confere propagação e rollback por address/tipo de primitiva, sem impor a ordem de mutex e condições.

Os testes da própria infraestrutura devem passar mesmo antes de completar o exercício:

```sh
python3 checks/test_support.py
python3 checks/test_queue_startup.py
```

O primeiro usa um compilador substituto que inicia um filho e verifica encerramento em timeout e interrupção.
Cada compilação real recebe sessão/grupo próprio; o supervisor encerra o grupo e executa reaping do driver nesses casos.
O teste usa subreaper somente em seu próprio processo Linux para também executar reaping do filho órfão do compilador substituto, e restaura esse atributo ao sair.
O segundo valida os wrappers com primitivas isoladas, incluindo rejeição de destruição após init falho e de destruição ausente.
Esses autotestes não implementam nem aprovam a fila do participante.

Complete os arquivos em [materials/starter](materials/README.md) e o modo ordered de [deadlock.c](experiments/deadlock.c).
Depois repita os checks e compare `python3 experiments/run.py --mode mutex` com `--mode atomic`.
Para escolher outro compilador, use `CC=clang python3 checks/check.py`.

TSan é opcional:

```sh
CC=clang python3 experiments/run.py --tsan
CC=clang python3 checks/check.py --tsan
```

No modo unsafe, um diagnóstico de data race é esperado quando a execução instrumentada o detecta.
TSan costuma retornar status não zero nesse caso; o script exibe stderr e para antes do deadlock.
Falha de linking ou inicialização do runtime não equivale a data race detectada. Registre a mensagem e a limitação do ambiente.
Os checks instrumentados usam apenas modos corretos do contador e a fila; não aprovam diagnósticos de data race.
TSan não prova ausência de data races e não é prova de ausência de deadlock.
Instrumentação altera agendamento e custo; não compare seus tempos com execuções normais como medida de contenção.

[O roteiro](experiments/README.md) orienta a interpretação. [As referências](references.md) explicam ferramentas e código real.
Use [o modelo local de relato](report-template.md) para separar hipótese de observação.
Código: MIT. Fixtures próprios: CC0-1.0. Documentação: CC BY 4.0.

## Interface Make

Execute da raiz deste laboratório, com GNU Make e Python 3.10+:

```sh
make help                 # Comandos, requisitos e seletores
make setup                # Verifica as ferramentas; não instala globalmente
make build                # Compila sem executar o exercício
make test                 # Checks da solução; o starter pode falhar
make run                  # Experimento padrão
make verify-preparation   # Verifica a preparação do starter original
make clean                # Limpa artefatos conhecidos; preserva resultados
```

`make` sem argumentos mostra ajuda. Veja os seletores `VARIANT`, `MODE` e
`EXPERIMENT` disponíveis em `make help`. Cada pacote funciona independentemente.
A interface exige Linux; requisitos de arquitetura seguem o roteiro acima.
Saídas de `run` ficam em um diretório novo de `results/`; falhas continuam visíveis.
Após modificar o starter, use `test`: `verify-preparation` compara a preparação
original e não comprova a correção da sua solução.

### Experimento e seletores deste laboratório

`make run` observa a corrida do contador e o deadlock controlado. Um timeout
previsto pelo observador demonstra o deadlock; não aprova a implementação.
Para explorar somente o modelo de interleavings:

```sh
make run EXPERIMENT=model
```

A variante Rust usa seus próprios checks:

```sh
make setup VARIANT=rust
make build VARIANT=rust
make test VARIANT=rust
make run VARIANT=rust
```

Na variante Rust, `run` demonstra o modelo de interleavings independente do
starter; `test` continua rejeitando a implementação incompleta.
