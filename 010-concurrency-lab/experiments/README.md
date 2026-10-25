# Investigar interleavings, contador e deadlock

Execute estes comandos na raiz do laboratório. Todos os prazos abaixo são limites de execução, não resultados medidos.

## Prever e observar o modelo

Separe incremento em ler, somar localmente e escrever. Desenhe duas interleavings para A e B.
Execute `python3 experiments/interleavings.py` e compare sua previsão com as 20 interleavings.
O script enumera um modelo sequencial explícito, no qual o resultado pode ser 1 ou 2.
Não conclua que um programa C com data race se limita a esses resultados: C define esse programa como UB.

## Comparar as variantes do contador

Execute `python3 experiments/run.py`. Registre compilador, flags, as três saídas e sua previsão.
Não exija perda de incrementos para reconhecer o defeito no código unsafe.
Depois de implementar, execute `python3 checks/check.py`, seguido de `python3 experiments/run.py --mode mutex` e `--mode atomic`.
Explique por que cada acesso conflitante é protegido e quando o coordenador pode ler a saída.
Justifique a ordem de memória do incremento atômico. O contador não publica outros dados; isso não autoriza a mesma escolha em uma fila.
Não transforme três saídas iguais em prova de correção, nem use o contador com UB como benchmark válido.
Se usar TSan, registre versão, comando, diagnóstico ou indisponibilidade do runtime, conforme [o guia](../README.md).

## Investigar deadlock

O script de execução inicia `deadlock bad` com timeout de 2 segundos.
Cada thread segura um lock diferente. A barrier com o coordenador estabelece esse estado antes da tentativa do segundo lock.
Registre o marcador e desenhe quem segura cada lock e de qual lock depende.
A evidência forte do ciclo vem dessa construção; um timeout isolado também poderia decorrer de lentidão ou falha do ambiente.
O supervisor encerra seu processo e executa seu reaping após o limite. Nenhum processo intencionalmente preso deve ficar em execução.

Complete `ordered` em [deadlock.c](deadlock.c). Preserve o cenário bad como comparação.
Estabeleça uma ordem global de aquisição e remova a barrier entre locks na variante corrigida.
Após reunir ambas as threads e destruir primitivas, emita `completed` e retorne zero.
Execute os checks. Explique como a ordem impede o ciclo; os testes finitos não provam ausência de todo deadlock possível.

## Registrar invariantes

Entregue uma tabela com campo, lock protetor, predicado de espera e evento que pode permitir progresso.
Inclua fila cheia, fila vazia, fechamento, drenagem e destruição.
Explique por que uma notificação não substitui reavaliar o predicado após acordar e por que encerramento interessa aos dois grupos.
Não há medição obrigatória de desempenho. Se medir como extensão, primeiro verifique correção e registre relógio monotônico, carga e repetições.
