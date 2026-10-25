# Experimento — Fronteiras de leitura

Antes de implementar, preveja quantas mensagens cada chamada de feed pode emitir.
Use o vetor binary: `4f4301010000000300ff41`, com 11 bytes no total.

O trace abaixo é **normativo**, deduzido dos bytes, não uma execução de solução:

| Plano | Bytes por chamada | Quantidades retornadas por chamada | EOF |
| --- | --- | --- | --- |
| whole | 11 | 1 | sucesso |
| bytes | onze chamadas de 1 | dez zeros, depois 1 | sucesso |
| mixed | 3,0,5,2,1 | 0,0,0,0,1 | sucesso |
| joined | 22, duas cópias | 2 | sucesso |
| truncated | 10 | 0 | truncated_payload |

Na oitava posição do plano bytes, o decoder conhece length=3, mas ainda não tem payload.
O chunk vazio do plano mixed preserva o header parcial.
Execute `python3 experiments/trace.py` após implementar. Salve a saída e compare cada linha com a tabela.
O script imprime `(flags, payload_hex)` para cada mensagem. Ele não decodifica o header por conta própria.

Depois, acrescente uma mensagem vazia após binary e divida exatamente no meio de cada header.
Registre as fronteiras e o número acumulado de mensagens. Finalize também após cada prefixo próprio de binary.

Explique as relações causais:

- Por que a leitura de oito bytes não conclui binary, mas conclui empty?
- Qual estado permite continuar quando length está dividido entre chunks?
- Por que um read de socket pode retornar duas mensagens ou só parte de uma?
- Por que `feed(b'')` nesta API não é a mesma operação que finish, embora uma leitura de transporte possa sinalizar EOF?
- Por que procurar magic dentro do payload após erro mudaria o contrato e poderia inventar uma mensagem?
- Se um encoder e um decoder usam little-endian por engano, qual vetor detecta o defeito que roundtrip pode esconder?
- Que cópias uma implementação que concatena bytes a cada chamada faz ao receber 4096 bytes um por vez?

O experimento modela fragmentação em memória. Não mede latência, syscalls ou comportamento do kernel.
