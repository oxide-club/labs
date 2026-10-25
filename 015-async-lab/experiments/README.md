# Experimento — Trace de tarefas e notificações

**Previsão:** leia [trace.rs](trace.rs) antes de executar. Escreva sua previsão
em uma seção separada do relato. O programa cria a tarefa `event` primeiro e
`yield` depois. Uma espera o sinal manual; a outra pede duas notificações no
primeiro poll. Preveja a fila após cada chamada e o efeito de sinalizar duas vezes.

**Comando**, a partir da raiz do laboratório:

```sh
python3 experiments/trace.py
```

**Observação:** guarde a saída real. As linhas `spawn` relacionam nomes a IDs;
`poll` e `result` registram a fronteira de execução da future; `wake` e `signal`
registram chamadas explícitas; `step` informa o resultado do executor.
Essas linhas não medem tempo nem registram a estrutura privada da fila.
No starter, a única observação disponível é o panic por implementação ausente.
Não apresente o trace previsto como saída obtida.

**Explicação:** compare previsão e saída depois de implementar. Mostre onde ocorre
`Idle`, por que ele não significa `Complete` e por que o wake durante poll não é
descartado. Relacione a alternância observada aos checks FIFO. Execute também o
check com produtor em outra thread para estudar a espera blocking em `run`.

**Limite:** este trace controla a ordem dos eventos na mesma thread. Ele não explora
todos os interleavings de sinalização concorrente e não prova ausência de busy-loop.
O wrapper termina o processo se ele ultrapassar cinco segundos.
