# Materiais

[O contrato](../index.md) define entradas, erros, sincronização e lifetime.
Os arquivos têm nomes em inglês; explicações usam Português Técnico Claro.

| Arquivo | Função |
| --- | --- |
| [starter/counter.h](starter/counter.h) | API do contador e modos. |
| [starter/counter.c](starter/counter.c) | Criação/join e incremento unsafe fornecidos; mutex/atomic incompletos. |
| [starter/queue.h](starter/queue.h) | API e espaço de implementação da fila. |
| [starter/queue.c](starter/queue.c) | Funções vazias que retornam ENOSYS, sem solução de sincronização. |
| [cases.json](cases.json) | Combinações independentes de capacidade, produtores, consumidores e itens. |
| [check.c](../checks/check.c) | Harness com IDs contados individualmente, FIFO, bloqueio e fechamento. |
| [startup.c](../checks/startup.c) | Injeção de falhas pthread por GNU linker --wrap; confere limpeza do contador. |
| [queue-startup.c](../checks/queue-startup.c) | Injeção por tentativa e rastreamento de rollback da fila, sem ordem fixa das primitivas. |
| [test_support.py](../checks/test_support.py) | Regressão de timeout/interrupção do compilador e de seu filho. |
| [test_queue_startup.py](../checks/test_queue_startup.py) | Autotestes do registro de primitivas, independentes da implementação da fila. |
| [support.py](../checks/support.py) | Compilação temporária e supervisão dos processos próprios. |

O produtor p gera IDs `p * items_per_producer + i`, com `0 <= i < items_per_producer`.
O conjunto esperado é `0..producers * items_per_producer - 1`; cada ID deve aparecer uma vez.
A comparação por ID detecta compensações que uma soma ou contagem total esconderia.
O harness usa atomics em seu registro de IDs para não introduzir uma data race no próprio verificador.

Os casos de bloqueio observam se uma operação terminou antes de liberar espaço ou inserir um item.
Uma flag indica que a thread começou a tentativa; um delay abre uma janela de observação.
O delay não comprova entrada em `pthread_cond_wait` e não controla o scheduler.
Fechamentos com quatro threads pendentes exercitam notificações de todos os interessados; revisão dos predicados permanece obrigatória.
Os testes de FIFO são sequenciais, pois ordem dos prints concorrentes não representa ordem de retirada.

Os programas C do pacote criam somente threads. Em falha de preparação do harness, ele encerra seu processo e suas threads.
O supervisor Python executa reaping do processo, inclusive em timeout ou Ctrl-C. Execuções corretas devem fazer join normalmente.
Nenhum check usa pkill, busca PIDs por nome ou encerra processos externos.
O compilador recebe timeout e sessão/grupo próprios. Em timeout ou interrupção, o helper envia SIGKILL somente ao grupo criado para essa compilação e executa reaping do driver.
Isso inclui subprocessos usuais como cc1, assembler e linker; ferramentas que saiam deliberadamente do grupo não fazem parte deste modelo. Arquivos executáveis ficam no diretório temporário e são removidos ao sair.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** Livre sob contrato de sincronização; por exemplo C, Rust, C++ e Go.

**Linguagens recomendadas:** Rust, C++ e Go.

**Restrições técnicas e plataforma:** Mutex, atomics e condition variables; fila limitada própria; sem canal pronto no mecanismo.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve IDs uint64, capacidades 1..64, FIFO, drenagem após close, notificação e join. Contador aceita 1..32 threads e 0..1000000 incrementos por thread; não substitua trabalho pelo produto. Result/Option e Drop podem substituir errno e destroy no contrato adaptado. Testes de nulos e rollback pthread continuam específicos de C. Rust seguro não reproduz a data race C; observe o diagnóstico original separadamente.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variante oficial adicional:** [starter rust](starter/rust/README.md).

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

O check de startup injeta falhas somente nas chamadas dinâmicas observadas; inicializadores estáticos POSIX são aceitos e não oferecem esse ponto de injeção. Revise seu lifetime. Os casos de contador incluem 8 threads × 1000000 incrementos; resultados sozinhos não distinguem o atalho proibido `threads*iterations`, que exige revisão do código.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
