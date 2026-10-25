# Operar notificações de laboratórios

O workflow `discord-contributions.yml` avisa sobre novas propostas em PRs
abertos para `main`. Ele reage a `opened`, `ready_for_review`, `synchronize`
e `reopened`. Um PR com vários laboratórios produz uma mensagem.

Configure `DISCORD_CONTRIBUTIONS_WEBHOOK_URL` como Actions Secret de
`oxide-club/labs`. O webhook deve apontar para `#contribuicoes`.
Incorpore os scripts e o workflow em `main` antes de esperar notificações:
o checkout usa o SHA da base do PR, nunca o código da contribuição.

## Recuperar um envio pendente

Antes do envio, o script reserva `pr:<número>` em `state.json`, na branch
`discord-state`. Depois da confirmação, salva o ID da mensagem.
Uma resposta perdida pode deixar a reserva pendente mesmo que a mensagem
tenha chegado. Novas execuções param para evitar duplicatas.

Confira o canal e identifique o PR. Em uma cópia confiável deste repositório,
use Node.js 24 e forneça `GH_TOKEN` pelo ambiente, com permissão de escrita
no conteúdo de `oxide-club/labs`. Não coloque tokens em arquivos versionados.

Se a mensagem chegou, registre o ID real da mensagem:

```sh
export GITHUB_REPOSITORY=oxide-club/labs
node scripts/discord/state.mjs record pr:42 ID_DA_MENSAGEM
```

Se confirmou que a mensagem não chegou, libere a reserva:

```sh
export GITHUB_REPOSITORY=oxide-club/labs
node scripts/discord/state.mjs release pr:42
```

Substitua `42` pelo número do PR. Depois reexecute o workflow. A liberação
pode duplicar uma mensagem se o envio anterior tiver chegado. Não apague
a branch nem recrie `state.json` para resolver falhas de permissão ou dados inválidos.

## Verificação local

```sh
node --test tests/discord-*.test.mjs
python3 -m unittest discover -s tests
python3 scripts/verify-cache-model.py
```

Os testes usam respostas locais para GitHub e Discord, sem credenciais
e sem mensagens reais. Para o sistema compartilhado, consulte a
[documentação do site](https://github.com/oxide-club/oxideclub.dev/blob/main/docs/DISCORD-NOTIFICATIONS.md).
Avisos em `#novidades` para labs ainda exigem suporte no site.
