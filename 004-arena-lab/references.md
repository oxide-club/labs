# Referências e leitura orientada

O contrato do enunciado é a especificação da atividade; os alocadores abaixo
possuem requisitos diferentes. Os arquivos PostgreSQL foram consultados no commit
`3d6a828938a5fa0444275d3d2f67b64ec3199eb7` (tag `REL_18_0`).

- [PostgreSQL: bump.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/utils/mmgr/bump.c)
  implementa um contexto de allocations sequenciais e descarte coletivo. Observe
  `BumpAlloc`, `BumpAllocChunkFromBlock`, `BumpReset`, `freeptr` e `MAXALIGN`.
  Diferente da arena fixa, ele administra múltiplos blocos e distingue pedidos grandes.
  Pergunta: qual estado o reset conserva para permitir reutilização do contexto?
- [PostgreSQL: aset.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/utils/mmgr/aset.c)
  implementa AllocSet com blocos e freelists para reutilizar chunks. Observe
  `AllocSetReset`, as listas por classe de tamanho e o tratamento dos pedidos grandes.
  Diferente do núcleo, admite reutilização individual e metadados mais complexos.
  Pergunta: por que manter diferentes políticas de contexto em vez de uma única arena?
- [OSTEP: Memory API](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-api.pdf) e
  [Free-Space Management](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-freespace.pdf)
  apoiam o estudo de propriedade e fragmentação. Compare espaço livre total com
  o tamanho do maior pedido atendível na extensão.
- [C11 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf),
  seções 6.2.8, 6.5 e 7.22.3, permite consultar alinhamento, tipo efetivo e allocation.
  Pergunta: por que um endereço numericamente alinhado não encerra a discussão
  sobre acesso a objetos por um tipo?

A preparação verificou os dois arquivos de código no commit fixo. As leituras
normativas e pedagógicas acima são consultas recomendadas; não foi feita revisão
integral desses documentos nesta preparação.
