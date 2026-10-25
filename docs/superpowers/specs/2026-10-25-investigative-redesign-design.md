# Revisão dos quatro laboratórios

Direção aprovada na conversa: consolidar 004 com challenges/017 e 009 com challenges/021; reformular 001 e 003 como investigações. A alternativa de ampliar os quatro como laboratórios manteria duplicações. Mover os quatro para challenges descartaria oportunidades investigativas próprias de representação e lifetime.

Decisões de implementação: preservar IDs e materiais históricos; adicionar `supersededBy` aos dois laboratórios consolidados. Eles deixam as listagens ativas; suas páginas encaminham ao desafio e seus downloads continuam acessíveis. O site deve validar o destino. Não haverá deploy, push ou renumeração.

001: fornecer um instrumento completo e independente do antigo starter. Comparar palavras com bytes distintos, ordens LE/BE e duas structs com mesmos campos em ordens diferentes. Formular hipóteses discriminantes, medir offsets/tamanhos e separar layout do host de formato externo. Implementar uma pequena alteração instrumental e registrar contraexemplos. Encoder histórico permanece opcional.

003: comparar alias válido, owner zerado com view ainda pendente, cópia independente e reset lógico de arena. Cada caso roda em processo próprio, com diagnóstico ASan onde aplicável. Não comparar numericamente saídas de UB. Formular hipótese sobre validade versus endereço/sanitizador; explicar o caso de reset sem erro ASan. Acrescentar uma intervenção segura e evidência causal. Correção histórica e CLI de offsets ficam opcionais.

Challenges: preservar APIs e testes obrigatórios. Incorporar orientação útil de invariantes, leitura de traces e diferenças entre variantes, sem exigir uma segunda implementação nem copiar contratos incompatíveis.

Conclusão exige documentação coerente, instrumentos executáveis, checks de preparação alinhados, validação editorial, testes das novas observações e testes do site para retirada, destino e manutenção de materiais.
