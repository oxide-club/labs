# Referências orientadas

Consulta em 25/10/2026. As referências ajudam a justificar invariantes; o contrato obrigatório está no [enunciado](index.md).

## Condições de espera e ferramentas

[OSTEP, capítulo 30 — Condition Variables](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf) apresenta espera por predicados e produtores/consumidores.
Observe como mudanças no estado afetam quem pode progredir. Pergunta: por que acordar não significa que o predicado ainda é verdadeiro?
O exercício acrescenta fechamento explícito, preservação de IDs e destruição após término das threads. Capítulo consultado.

[Clang — ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html) descreve instrumentação para encontrar data races em execuções observadas.
Observe flags, plataformas e restrições do runtime. Pergunta: por que um programa instrumentado sem diagnóstico ainda precisa de análise dos acessos?
TSan altera a execução e não substitui um argumento sobre progresso. Documentação consultada; a execução local e seus resultados constam do registro de preparação.

## Código real: Crossbeam

[Crossbeam — crossbeam-channel/src/flavors/array.rs, revisão 7b573a0301089e346a4082e6f403cc2b271353c4](https://github.com/crossbeam-rs/crossbeam/blob/7b573a0301089e346a4082e6f403cc2b271353c4/crossbeam-channel/src/flavors/array.rs) implementa um canal limitado sobre um array em Rust.
O SHA foi identificado no [histórico do arquivo](https://github.com/crossbeam-rs/crossbeam/commits/main/crossbeam-channel/src/flavors/array.rs).
A página fixada e o conteúdo raw não puderam ser recuperados nesta consulta; o arquivo foi inspecionado na [página main](https://github.com/crossbeam-rs/crossbeam/blob/main/crossbeam-channel/src/flavors/array.rs), que pode mudar.
Não se afirma comparação byte a byte entre a revisão fixada e main. A página do commit retornou HTTP 429.

Observe `start_send`, `start_recv`, estados por slot e as operações atômicas que coordenam publicação e leitura.
Examine `disconnect_senders` e o caminho de recepção que ainda verifica mensagens restantes após desconexão.
A diferença importa: o código real usa protocolos atômicos, seleção de operações e desconexão de remetentes/receptores; o exercício pede mutex e condições com um único close explícito.
Pergunta de leitura: que estado permite distinguir fila vazia temporária de encerramento e que operação permite observar o item publicado?
Não copie esse algoritmo antes de justificar os invariantes da fila simples. Nenhum código de terceiro foi incorporado ao pacote.
