# Materiais — Execução Assíncrona

[executor.rs](executor.rs) fixa as assinaturas de `Executor`, `TaskId` e `Step`.
Fila, estado das tarefas, Waker e espera blocking são trabalho do participante.
[event.rs](event.rs) fixa a API de uma future de evento manual e de sua extremidade
de sinalização. Ambos compilam com `todo!`, mas não implementam o mecanismo central.
O [contrato](../index.md) determina as transições observáveis.

`Wake` com `Arc` permite construir um Waker sem `unsafe`. O estado alcançado pelo
Waker deve aceitar acesso entre threads, enquanto as futures podem conter `Rc`.
Escolha como representar essa separação e explique por que um wake não executa poll.
Não consulte todas as tarefas repetidamente para descobrir quais estão prontas.

Os [checks públicos](../checks/public.rs) definem uma future controlada independente:
ela conta polls, guarda o último Waker e só fica pronta quando o teste muda seu estado.
Não use essa future como implementação de `event.rs`. A assinatura de `spawn`
e o teste com `Rc` exigem suporte a futures sem `Send`.

| Caso | Evidência exigida |
| --- | --- |
| Vazio e reutilização | Termina sem esperar canais; IDs não são reutilizados |
| Pending e duplicações | Nenhum poll sem sinal; cem wakes viram uma oportunidade |
| Wake durante poll | Sinal não se perde; duas tarefas alternam pela fila FIFO |
| Wake após Ready | Future foi liberada e não recebe outro poll |
| Wake seletivo e destruição | Outra tarefa pendente permanece intocada; drop libera futures |
| Thread produtora | Só a thread do executor faz poll; run espera e termina após sinal |
| Evento manual | Sinal anterior ao poll persiste; Waker mais recente recebe o sinal |

A janela de 50 ms do teste com thread apenas permite observar uma tarefa pendente;
o canal sincroniza o primeiro poll e um lock publica o evento. Não se mede desempenho
nem se exige um tempo de conclusão de 50 ms. O limite externo protege o teste.
Um check Linux adicional observa uma janela de 300 ms após o primeiro poll: menos de 100 ms de CPU e menos de 80 trocas voluntárias de contexto na thread do executor. Isso rejeita spin contínuo e sleep-polling de 1 ms; não prova ausência de todo polling possível. Requer procfs (`/proc/thread-self/stat` e `status`) e `getconf CLK_TCK`. Revise a primitiva de espera, seu predicado e as races que os testes não enumeram.

Dos dez checks no Linux, um é autoteste da fixture e nove exercitam o contrato. Outro teste reentra em `signal` a partir do Waker, verificando liberação do lock antes de `wake`.

## Linguagens e ambiente

**Linguagem de referência:** Rust.

**Linguagens aceitas:** Rust para Future/Poll/Waker; C e C++20 como comparações de outro modelo.

**Linguagens recomendadas:** Rust; C++20 para comparação.

**Restrições técnicas e plataforma:** Rust 2021/std; executor single-threaded próprio; sem Tokio ou runtime pronto.

**Tipo de equivalência:** apenas comparativa entre modelos; Rust é o núcleo atual.

### Contrato independente da linguagem

O checkout já fornece executor.rs e event.rs, checks e trace. Preserve Future, Poll, Context, Waker, coalescing e espera blocking. C não tem esses traits: um estado pendente e callbacks não demonstram o mesmo contrato de Pin, ownership e Wake. Não há executor C neste pacote; a comparação é conceitual, sem alegar teste cruzado.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variante oficial:** os starters Rust `executor.rs` e `event.rs` já existentes. Não há executor C neste pacote.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

### Comparação de modelos

| Questão | Executor de estados em C (comparação conceitual) | Núcleo Rust deste pacote |
| --- | --- | --- |
| Retomar trabalho | Estado explícito e chamada a uma função definida pela aplicação | `Future::poll` recebe `Context` e retorna `Poll` |
| Avisar prontidão | Callback/fila definidos pelo contrato da aplicação | `Waker` solicita nova oportunidade; wake não executa poll |
| Posição e lifetime | O programa deve definir estabilidade e validade dos ponteiros | `Pin` e ownership delimitam acesso à future armazenada |
| Pendência | Estado pendente exige protocolo próprio de notificação | `Pending` não autoriza consultar repetidamente sem wake |
| Conclusão | A aplicação define liberação e descarte de notificações tardias | O executor libera a future e ignora wakes de tarefa concluída |

Essas correspondências ajudam a formular perguntas, mas não demonstram
equivalência integral. Não há implementação C aqui para executar uma comparação.
C++20 e outros modelos exigem contrato próprio antes de comparar progresso,
lifetime, cancelamento ou custos. Os dez checks no Linux verificam o modelo
Rust; não certificam outro runtime.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
