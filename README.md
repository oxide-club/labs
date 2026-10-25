# Laboratórios do Oxide Club

Cada laboratório propõe uma investigação. A entrega inclui código, resultados observados e uma explicação.
Cada diretório numerado contém um roteiro em `index.md`, materiais e verificações.
O site lê os arquivos deste repositório.
Não edite a cópia gerada em `.content/labs`.

Consulte a [política de linguagens](docs/politica-de-linguagens.md).
C permanece a referência onde já existe; linguagens aceitas não significam
starters oficialmente mantidos. VM, protocolos e atenção têm referência Python;
async já tem referência Rust neste checkout.

Para verificar somente uma preparação adicional, execute
`python3 scripts/verify-variants.py --variant cache-rust`.
Os demais seletores são `vm-rust`, `protocol-go`, `concurrency-rust`, `async-rust`
e `gpu-cuda` (somente build, sem validação de kernels). Não é necessário instalar
todas as toolchains. Para uma atividade existente, use
`python3 scripts/verify-preparation.py --lab 001-binary-lab`, trocando o ID.

## Catálogo

O catálogo mantém 16 laboratórios ativos e dois registros históricos consolidados em desafios.
Os IDs 004 e 009 não são reutilizados. `supersededBy` retira esses registros das listagens
ativas no site compatível, preservando a página, seus materiais e o destino do desafio.
O estado `published` registra publicação anterior; esta revisão local ainda precisa ser integrada ao site.
Os starters de implementação continuam incompletos por desenho.
Os instrumentos de observação de 001 e 003 estão completos e independem dos starters históricos.
O [registro de IDs](docs/catalogo.json) mantém a correspondência com o currículo.

| Laboratório | Estado |
| --- | --- |
| [001 — Representação Binária](001-binary-lab/index.md) | Publicado |
| [002 — Engenharia Reversa](002-reverse-engineering-lab/index.md) | Publicado |
| [003 — Segurança de Memória](003-memory-safety-lab/index.md) | Publicado |
| [004 — Alocação de Memória](004-arena-lab/index.md) | Consolidado no desafio 017 — Arena |
| [005 — Cache e Localidade](005-cache-lab/index.md) | Publicado |
| [006 — Processos e Pipes](006-processes-lab/index.md) | Publicado |
| [007 — Compilação e Execução](007-compilation-lab/index.md) | Publicado |
| [008 — Multiplicação Matricial](008-matrix-lab/index.md) | Publicado |
| [009 — Máquinas Virtuais](009-vm-lab/index.md) | Consolidado no desafio 021 — Bytecode |
| [010 — Concorrência e Sincronização](010-concurrency-lab/index.md) | Publicado |
| [011 — Protocolos Binários](011-protocol-lab/index.md) | Publicado |
| [012 — ABI e Calling Conventions](012-abi-lab/index.md) | Publicado |
| [013 — Syscalls](013-syscalls-lab/index.md) | Publicado |
| [014 — Bibliotecas Compartilhadas e Linking Dinâmico](014-dynamic-linking-lab/index.md) | Publicado |
| [015 — Execução Assíncrona](015-async-lab/index.md) | Publicado |
| [016 — Isolamento de Processos](016-isolation-lab/index.md) | Publicado |
| [017 — Computação Paralela em GPU](017-gpu-lab/index.md) | Publicado |
| [018 — Mecanismos de Atenção](018-attention-lab/index.md) | Publicado |

### Novos laboratórios aprovados

As cinco propostas abaixo têm pacotes executáveis preparados e verificados. Estão aprovadas para publicação, com `draft: false`; a publicação no website depende da integração e do deploy. Os READMEs de cada laboratório descrevem os comandos, materiais e limites de execução.

| Laboratório | Estado |
| --- | --- |
| [019-atomics-lab — Atomics e memory ordering](019-atomics-lab/index.md) | Aprovado para publicação |
| [020-dispatch-lab — Monomorfização e dynamic dispatch](020-dispatch-lab/index.md) | Aprovado para publicação |
| [021-fuzzing-lab — Fuzzing e análise de falhas](021-fuzzing-lab/index.md) | Aprovado para publicação |
| [022-page-protection-lab — Page protection e access violations](022-page-protection-lab/index.md) | Aprovado para publicação |
| [023-elf-hardening-lab — Evidências de hardening em executáveis ELF](023-elf-hardening-lab/index.md) | Aprovado para publicação |

Os números identificam os laboratórios. Você pode escolher a ordem de estudo.

Cada README local informa dependências e comandos. Isolamento exige VM descartável para execução.
O CI usa verificações CPU de GPU; isso não substitui compilação e execução CUDA.

## Verificação editorial

1. Execute `python3 -m unittest discover -s tests`.
2. Execute `python3 scripts/verify-cache-model.py`.
3. Execute `python3 scripts/prepare-reports.py --check`.
4. Execute `python3 scripts/validate.py`.
5. Execute `python3 scripts/verify-preparation.py`.

O último comando distingue falhas esperadas do starter de erros na preparação.
Use `--lab ID` para limitar a atividade e `--json CAMINHO` para guardar evidências completas.
As verificações declaradas ficam em `docs/preparation-checks.json`; elas não substituem os checks da solução.

Ao atualizar o template de relato, execute `python3 scripts/prepare-reports.py`.
Após conferir alterações intencionais em fixtures, atualize seus hashes com `python3 scripts/validate.py --update-fixtures`.
O hash detecta alterações; não demonstra correção semântica.
O website faz a validação completa do schema YAML durante o build.

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

## Áreas de interesse

Cada roteiro, inclusive rascunhos, declara uma única `area` com um ID de
`areas.json`. O registro define título, descrição, slug e ordem das áreas no site.
Escolha a área principal pela pergunta central e pela investigação exigida no
roteiro. Use `topics` para conceitos transversais, como desempenho, segurança,
memória e ponto flutuante; a linguagem ou ferramenta utilizada não determina a área.
Percursos de estudo podem atravessar áreas e não definem a classificação.
Não renumere atividades ao mudar sua área. Atualize o registro para criar áreas.

| Área | Escopo | Laboratórios atuais |
| --- | --- | --- |
| Representação de dados e protocolos | Codificação, serialização e reconhecimento de mensagens em bytes. | 001, 011 |
| Memória e localidade | Tempo de vida, alocação, validade dos acessos e comportamento da cache. | 003, 005 |
| Compilação e execução de programas | Transformação, interpretação, linking e análise de código executável. | 002, 007, 012, 014 |
| Sistemas operacionais e processos | Interfaces do kernel, processos, recursos e isolamento. | 006, 013, 016 |
| Concorrência e paralelismo | Progresso de tarefas, sincronização e distribuição de trabalho. | 010, 015, 017 |
| Computação numérica | Operações matemáticas, custo computacional, memória e precisão. | 008, 018 |

## Comandos locais padronizados

Cada pacote tem um Makefile independente. Comece com `make help` na raiz do
laboratório. Use `setup`, `build`, `test`, `run`, `clean` e `verify-preparation`.
Os starters incompletos continuam falhando em `test`. Evidências de `run` ficam
em `results/`, preservado por `clean`. GNU Make, Python 3.10+ e Linux são requisitos
da interface; toolchains e hardware dependem da atividade e variante.

Os laboratórios 002, 003 e 016 executam em VM descartável preparada por
`make env-setup`; `make env-shell` permite inspeção e confirmação no guest.
A imagem Alpine e cada pacote têm hash fixado; os experimentos rodam sem rede.

Mantenedores: edite `docs/make-labs.json` e `templates/make/`; execute
`python3 scripts/prepare-make.py` e confira `python3 scripts/prepare-make.py --check`.
A preparação local reutiliza cópias geradas do verificador e dos manifests
editoriais. Após mudanças intencionais nos manifests distribuídos, atualize seus
hashes com `python3 scripts/validate.py --update-fixtures`.
