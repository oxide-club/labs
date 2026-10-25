# Laboratórios do Oxide Club

Cada laboratório propõe uma investigação. A entrega inclui código, resultados observados e uma explicação.
Cada diretório numerado contém um roteiro em `index.md`, materiais e verificações.
O site lê os arquivos deste repositório.
Não edite a cópia gerada em `.content/labs`.

## Catálogo

- 005 — Laboratório de Cache e Localidade: disponível neste repositório.

## Nomes reservados

- 001 — Laboratório de Representação Binária
- 002 — Laboratório de Engenharia Reversa
- 003 — Laboratório de Segurança de Memória
- 004 — Laboratório de Alocação de Memória
- 006 — Laboratório de Processos e Pipes

Os números identificam os laboratórios. Você pode escolher a ordem de estudo.

## Verificação editorial

1. Execute `python3 -m unittest discover -s tests`.
2. Execute `python3 scripts/verify-cache-model.py`.

O modelo independente verifica os resultados esperados dos experimentos.
O pacote do participante não inclui esse modelo.

Consulte [contribuição](CONTRIBUTING.md) e [licenças](LICENSING.md).

## Notificações no Discord

PRs prontos para revisão que adicionam `NNN-nome/index.md` são divulgados
em `#contribuicoes`, com título e link para o PR. PRs em draft aguardam
a passagem para pronto. Atualizações e reaberturas não repetem avisos
já confirmados. Edições, materiais isolados e renomeações não são novas propostas.
O campo `draft` do conteúdo não impede a divulgação de uma proposta para revisão.

Mantenedores devem configurar o Actions Secret `DISCORD_CONTRIBUTIONS_WEBHOOK_URL`
neste repositório, apontando para o webhook de `#contribuicoes`. O workflow
usará o código da base confiável do PR, inclusive para contribuições de forks.
Ele precisa de `contents: write` para registrar os envios e de `pull-requests: read`
para consultar os arquivos. A branch `discord-state` é criada automaticamente,
com histórico em `state.json`. Não apague esse histórico.

Se um envio ficar pendente, confira o canal antes de tentar novamente.
Consulte [docs/DISCORD-NOTIFICATIONS.md](docs/DISCORD-NOTIFICATIONS.md) para recuperação.

Execute os testes sem enviar mensagens: `node --test tests/discord-*.test.mjs`,
com Node.js 24. Os módulos de `scripts/discord/` seguem o padrão de `notes`
e `challenges`, com suporte adicional ao repositório e aos identificadores de labs.

Avisos de publicação em `#novidades` dependem do repositório do site.
A implementação atual do site contempla apenas desafios e notas;
este workflow divulga propostas de laboratórios para revisão.
