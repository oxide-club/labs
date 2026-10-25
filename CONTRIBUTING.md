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
Os formatos aceitos seguem a lista explícita de distribuição descrita abaixo.
Não inclua programas compilados, dependências, segredos ou links simbólicos.
Descreva cada arquivo em `materials/README.md`.
Informe a origem e a licença dos materiais.

Para ocultar resultados de conferência, use `<details><summary>Conferir resultados</summary>…</details>` sem atributos.
Mantenha as instruções obrigatórias fora desses blocos.

## Português Técnico Claro

Siga o [guia de redação](docs/guia-de-redacao.md) e o [glossário](docs/glossario-tecnico.md).
A convenção é interna ao clube; não declara conformidade com o ASD-STE100.
Revise primeiro o contrato e os exemplos. Depois, revise clareza e terminologia.
Use o [checklist de publicação](templates/publication-checklist.md).

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

## Preparar um laboratório

1. Consulte o [registro do catálogo](docs/catalogo.json) e reserve um ID sem renumerar os existentes.
2. Identifique a modalidade e escreva o contrato antes de preparar o starter.
3. Use os templates de [enunciado](templates/index.md), [README](templates/README.md), [referências](templates/references.md) e [relato](templates/report-template.md).
4. Prepare materiais concretos: código, entradas, fixtures, checks e experimentos necessários ao mecanismo.
5. Defina entradas, saídas, limites, erros, estados após falhas e invariantes.
6. Execute os comandos documentados em uma cópia dos materiais do participante.
7. Registre decisões, evidências e limitações na descrição do pull request ou em evidências de CI.
8. Mantenha `draft: true` durante a revisão, inclusive quando a infraestrutura passar nos testes.

Os seis originais preservam os contratos do Anexo A do currículo.
Por decisão do responsável, os fontes históricos `porta.c` e `vida.c` recebem os nomes `gate.c` e `lifetime.c`.
A mudança de nome não altera mensagens, entradas, resultados nem o objetivo da investigação.

Os testes do participante podem falhar no starter incompleto.
O CI deve conferir a preparação e os fixtures sem publicar soluções para obter sucesso.
Compare vetores independentes; round-trip sozinho pode esconder erros simétricos.
Antes de aprovar a preparação, execute os checks contra uma implementação privada correta
e pelo menos cinco mutantes que violem requisitos distintos. Registre comandos, resultados
e hashes dos fontes na descrição do pull request ou em evidências de CI. Não distribua essas soluções.
Para observação ou diagnóstico, documente os alvos e as variações controladas equivalentes.
Justifique quando a atividade não comportar cinco mutantes distintos.
Não use tempo universal, PID, endereço ou assembly literal como critério de correção.

## Distribuir e revisar

O empacotador do website inclui `materials/`, `checks/`, `experiments/`, enunciado, README, referências e relato.
Makefiles, arquivos de documentação e fontes C, Python, Rust, assembly, CUDA e TOML são aceitos pela lista explícita do website.
Fontes Go (`.go`) e o arquivo exato `go.mod` também são distribuídos.
Não distribua outros arquivos `.mod`, caches ou binários Go.
Não inclua executáveis, build, target, dependências, soluções ou dados temporários nesses diretórios.
O pacote deve incluir licenças e identificar a revisão.

O modelo de relato é compartilhado em `templates/report-template.md`.
O script de preparação gera cópias identificadas para pacotes independentes; não as edite manualmente.

Soluções da comunidade permanecem em repositórios dos participantes ou no fluxo próprio de soluções.
Um PR de materiais não deve incorporar automaticamente uma solução completa.
Mudanças de publicação exigem revisão humana e data real; preparar drafts não autoriza deploy.

## Linguagens e variantes

Siga a [política de linguagens](docs/politica-de-linguagens.md). Preserve IDs,
contratos originais e caminhos publicados. Acrescente “Linguagens e ambiente”
como H3 dentro de “Antes de começar”; não acrescente campos ao frontmatter.
Novos starters usam diretórios de linguagem. Materiais históricos permanecem em
seus caminhos para não quebrar pacotes e links; não duplique fontes por estética.
Compartilhe fixtures e checks comportamentais. Mantenha testes de API, memória,
ABI e runtime separados quando a linguagem fizer parte do contrato.

Antes de declarar uma variante oficial, verifique build, exemplos, fixtures,
rejeição esperada do starter e distribuição do pacote. Registre o que não foi
executado. Um starter incompleto não deve passar nos checks de conclusão.
