# Contribuir

1. Copie `templates/index.md` para o diretório do novo laboratório.
2. Use um identificador no formato `NNN-nome`.
3. Preserve os oito títulos de nível 2, na ordem do modelo.
4. Use títulos de nível 3 para os experimentos.
5. Descreva a pergunta, a preparação, os materiais e os resultados que o participante deve registrar.
6. Defina os critérios das etapas obrigatórias.
7. Coloque as extensões na seção de atividades opcionais.

Para uma simulação, não exija medições de uma CPU real.
Mantenha `draft: true` enquanto o conteúdo, os materiais e as verificações estiverem em revisão.
Antes de publicar, informe a data real em `publishedAt: YYYY-MM-DD`.

## Compartilhar uma investigação

1. Publique o código e o relato em um repositório seu.
2. Compartilhe o link na conversa do clube.

Inclua a previsão, os comandos, o ambiente, os resultados observados e sua conclusão.
Você pode compartilhar uma tentativa incompleta.
Para uma dúvida, mostre o menor exemplo que permite repetir o problema.
Você não precisa concluir as extensões para participar.

Envie melhorias por pull request neste repositório.
Ao propor uma solução, identifique o conteúdo como solução.
Inclua os resultados que sustentam sua explicação.
Mantenha os materiais iniciais separados da solução.
Ainda não há um catálogo automático de soluções dos laboratórios.

## Materiais

Use links relativos para `materials/`, `checks/` e `report-template.md`.
Os formatos aceitos são texto, C, arquivos de cabeçalho, Python, JSON e CSV.
Não inclua programas compilados, dependências, segredos ou links simbólicos.
Descreva cada arquivo em `materials/README.md`.
Informe a origem e a licença dos materiais.

Para ocultar resultados de conferência, use `<details><summary>Conferir resultados</summary>…</details>` sem atributos.
Mantenha as instruções obrigatórias fora desses blocos.

## Escrever textos claros

Adaptamos princípios do [ASD-STE100](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf) para textos em português.
Esta adaptação não declara conformidade formal com o padrão de inglês técnico.

- Use frases curtas. Nas instruções, procure limitar cada frase a 20 palavras.
- Escreva uma ação por frase. Use passos numerados quando a ordem for importante.
- Comece instruções com verbos diretos, como “execute”, “registre” e “compare”.
- Se uma ação depender de uma condição, escreva a condição antes da ação.
- Use o mesmo termo para o mesmo conceito. Explique termos técnicos antes de usá-los nas instruções.
- Separe explicações, instruções e resultados esperados.
- Preserve nomes de arquivos, comandos, fórmulas e valores ao revisar a linguagem.

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
