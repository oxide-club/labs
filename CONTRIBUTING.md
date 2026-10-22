# Contribuir

Use `templates/index.md` e um identificador estável `NNN-nome`.
Preserve os oito títulos de nível 2 e sua ordem. Use nível 3 para experimentos.
Declare a pergunta, preparação, arquivos, evidências e critérios do núcleo.
Separe extensões; não exija resultados de CPU real para um modelo simulado.
Use `draft: true` até que conteúdo, materiais e verificações sejam revisados.
Uma publicação exige `publishedAt: YYYY-MM-DD`; não invente datas de encontros.

## Compartilhar uma investigação

Publique código e relato em um repositório seu e compartilhe o link na conversa
do clube. Inclua hipótese, comandos, ambiente, evidência e conclusão, mesmo que
sua tentativa esteja incompleta. Para uma dúvida, mostre o menor caso reproduzível.
Não é necessário concluir extensões para participar.

Envie melhorias por pull request neste repositório. Uma proposta de solução deve
vir acompanhada das evidências e ser identificada como solução, sem substituir
os materiais iniciais. Não existe catálogo automático de soluções de labs ainda.

## Materiais

Use links relativos para `materials/`, `checks/` e `report-template.md`.
Forneça arquivos de texto, C, headers, Python, JSON ou CSV; não inclua binários,
dependências, segredos ou symlinks. Documente cada arquivo em `materials/README.md`.
Conferências podem usar `<details><summary>Conferir resultados</summary>…</details>`
sem atributos; não esconda instruções essenciais. Declare origem e licença.
