# Checklist de publicação

Use o [guia PTC](../docs/guia-de-redacao.md) e o [glossário](../docs/glossario-tecnico.md).
Registre evidências na descrição do pull request ou em artefatos de CI.

## Contrato e pedagogia

- [ ] Pergunta central, motivação, pré-requisitos e ambiente explícitos.
- [ ] Interfaces, entradas, saídas, erros, limites e invariantes definidos.
- [ ] Cada etapa tem ação, evidência e critério de verificação.
- [ ] O participante pode começar sem orientação externa.
- [ ] O starter não resolve o mecanismo central.
- [ ] As perguntas exigem explicações causais.
- [ ] O núcleo termina independentemente das extensões.

## Materiais e experimentos

- [ ] Compilação e execução repetidas com os comandos documentados.
- [ ] Fixtures independentes e casos-limite conferidos.
- [ ] Falhas intencionais distinguidas de falhas de infraestrutura.
- [ ] Checks verificam comportamento, sem impor detalhes internos arbitrários.
- [ ] Checks aceitam uma implementação privada correta e rejeitam pelo menos cinco mutantes distintos, ou há justificativa de não aplicabilidade.
- [ ] Comandos, resultados e hashes privados registrados; soluções ausentes do pacote.
- [ ] Correção verificada antes de medir desempenho.
- [ ] Medições identificam ambiente e não usam metas universais de tempo.
- [ ] Restrições de VM, GPU e permissões documentadas e verificadas quando aplicáveis.
- [ ] Pacote extraído funciona sem depender do checkout do autor.
- [ ] Referências de código foram consultadas e revisões registradas.

## Revisão PTC

- [ ] Frases diretas; instruções com verbos de ação.
- [ ] Termos consistentes e conceitos novos definidos.
- [ ] Deve, não deve, recomenda-se e pode usados com precisão.
- [ ] Condições e exceções preservadas; exemplos corretos.
- [ ] Revisão técnica e editorial realizadas separadamente.

## Publicação

- [ ] ID/slug, oito seções H2, links e licenças validados.
- [ ] Pacote inclui revisão e avisos, sem soluções ou artefatos temporários.
- [ ] Matriz registra resultados reais e verificações pendentes.
- [ ] Revisão humana de publicação concluída.
- [ ] Alteração explícita de draft e data real de publicação aprovada.

Uma caixa pendente não pode ser marcada apenas porque o CI passou.
Preparar o material não autoriza publicar automaticamente o catálogo.
