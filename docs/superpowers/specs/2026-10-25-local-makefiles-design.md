# Interface local de execução dos laboratórios

Estado: proposta para aprovação. Data: 2026-10-25.

## Intenção e decisões

Oferecer os mesmos comandos nos 18 laboratórios, tanto no checkout quanto no
pacote baixado. O participante deve conseguir preparar o ambiente, compilar,
testar e executar sem descobrir uma CLI diferente em cada atividade.

O responsável escolheu Make e Makefiles locais. Os detalhes abaixo são propostas
de implementação, incluindo a divisão da entrega em etapas.

## Abordagens consideradas

- Makefiles locais: alguma repetição, mas pacotes independentes e reaproveitamento
  dos builds existentes. Abordagem escolhida.
- Makefile central incluído pelos laboratórios: reduz repetição, mas cria uma
  dependência externa ao pacote. Descartado para a interface do participante.
- Just como interface: oferece recursos próprios de execução de tarefas, mas
  acrescentaria uma ferramenta aos laboratórios que já compilam com Make.
  O responsável confirmou a preferência por Make.

## Contrato dos comandos

O diretório de trabalho é a raiz do laboratório. `make` sem argumentos mostra
ajuda. Os alvos de ação são `.PHONY`; arquivos compilados mantêm dependências
reais quando o build existente já as representa.

| Alvo | Contrato |
| --- | --- |
| `help` | Lista alvos, seletores disponíveis, dependências e limitações. Não compila nem executa o exercício. |
| `setup` | Verifica ferramentas, plataforma e recursos do modo selecionado. Prepara somente diretórios locais necessários. Não instala pacotes globais, não usa sudo e não executa starters. |
| `build` | Compila sem executar o exercício. Para Python puro, informa que não há etapa de compilação; validação sintática pode ser usada sem importar o starter. |
| `test` | Executa os checks públicos do participante e propaga falhas. Pode preparar o build necessário. |
| `run` | Executa o experimento padrão documentado, com limites e supervisão já exigidos pelo roteiro. Pode preparar o build necessário. |
| `clean` | Remove somente artefatos conhecidos da infraestrutura local. Preserva fontes, fixtures, relatos e evidências. |
| `verify-preparation` | Verifica infraestrutura e condições conhecidas do starter, separadamente dos critérios de solução. Indica explicitamente a cobertura realizada. |

Falhas de dependência, compilação, runtime ou timeout nunca se tornam sucesso
silencioso. Os comandos mostram mensagens compreensíveis; não há promessa de
preservar o número exato do status do processo filho através do próprio Make.

`test` não chama o verificador editorial como substituto dos checks. Uma falha
esperada de um starter continua sendo falha em `test`. No laboratório 003,
`run` observa o defeito original, enquanto `test` verifica sua correção; essa
diferença deve aparecer em `help` e no README.

## Implementação e autonomia dos pacotes

Cada laboratório recebe um Makefile na raiz. Ele chama os scripts locais e,
onde existir, o Makefile de `materials/` por meio de `$(MAKE)`. Não haverá
includes, imports ou comandos dependentes de diretórios pais ou de `.git`.

Preservar caminhos publicados, contratos, fixtures, starters e comandos antigos.
Não mover arquivos para uniformizar apenas sua aparência. Scripts auxiliares
ficam em `materials/`, `checks/` ou `experiments/`, conforme a responsabilidade.
Preferir Python para lógica que ultrapasse receitas pequenas de shell.

A lógica de `verify-preparation` deve usar as verificações já declaradas em
`docs/preparation-checks.json`, adaptadas ao pacote local. O construtor decidirá
entre extração de dados e geração de cópias locais, mantendo uma fonte canônica
no repositório e uma verificação contra divergência. O pacote não exige o
manifesto central nem presume que código já editado ainda seja o starter.
Modificações pelo participante podem invalidar a observação esperada do starter;
a mensagem explica isso e orienta o uso de `test`.

As linguagens de referência são o padrão. Seletores de variante somente expõem
as variantes oficiais existentes: cache Rust, VM Rust, concorrência Rust e
protocolo Go. Async já é Rust. Escolher a variante não exige as demais toolchains.
Usar `VARIANT=reference` como padrão e nomes de linguagem nas variantes adicionais.
Um seletor desconhecido é erro, inclusive em setup.

No laboratório GPU, usar `MODE=cpu` ou `MODE=gpu`, com GPU como padrão dos alvos
de execução e testes da atividade. Sem hardware/toolchain, informar o requisito
e falhar. O modo CPU é explicitamente auxiliar e nunca aprova kernels CUDA.

Experimentos adicionais podem usar `EXPERIMENT=nome`, com nomes e argumentos
documentados localmente. Evitar uma API universal de parâmetros para todos os
experimentos. Honrar seletores existentes como `CC` onde suportados; não anunciar
variáveis que os scripts efetivamente ignoram.

## Artefatos e evidências

Reutilizar diretórios de build existentes. Novos artefatos ficam em `build/`
ou `materials/build/`, conforme o laboratório. Evidências persistentes ficam em
`results/`, em diretórios novos por execução, fora da limpeza normal.
Os scripts que já exigem destino novo continuam recusando sobrescrita.

O alvo `clean` usa uma lista explícita de caminhos locais gerados. Não apaga
destinos externos configurados pelo participante nem segue links simbólicos.
Não usa curingas amplos para remover arquivos de trabalho.

## Ambientes isolados e reproduzíveis

A interface deve suportar os ambientes sem alterar o contrato dos alvos. A
implementação terá duas etapas no mesmo escopo: primeiro os comandos locais;
depois o ambiente reproduzível e a integração dos laboratórios 002, 003 e 016.

Proposta: usar uma VM Linux x86-64 descartável com QEMU para esses três casos.
Reaproveitar como referência os requisitos documentados do laboratório 016.
O ambiente deve satisfazer ASan/LSan no 003 e os recursos de procfs/subreaper no
016. Não adotar containers como substitutos dessa VM. Containers para outros
laboratórios ficam fora desta entrega inicial.

Cada pacote desses três laboratórios incluirá receita local de preparação,
manifesto de versões e checksums e instruções de recuperação. Scripts comuns
podem ser mantidos em um template e distribuídos como cópias verificadas.
Não distribuir imagens ou binários no repositório ou pacote.

`make env-setup` obtém e verifica os insumos e prepara a imagem; é uma ação
explícita, separada de `setup`. `make env-shell` abre o ambiente descartável.
`make env-clean` remove somente os artefatos de ambiente gerados localmente.
Os comandos `test` e `run` desses três laboratórios devem encaminhar a execução
ao ambiente preparado; sem ambiente, falham com orientação para `env-setup`.
O mesmo vale para etapas dinâmicas de `verify-preparation`; esse alvo não pode
abrir um caminho alternativo de execução no host.
O fluxo interno do guest deve evitar recursão para o host.

Copiar apenas os materiais da atividade para o guest; não compartilhar home,
credenciais, sockets de serviços ou diretórios amplos do host. Executar como
usuário sem privilégios. Desabilitar rede durante os experimentos. Exportar
evidências por um canal limitado à pasta de resultados. Usar imagem base
verificada e estado descartável por sessão. Fixar imagem, toolchains e insumos
de instalação; registrar suas versões nas evidências. Checksums ou versões
indisponíveis impedem declarar a preparação reproduzível.

Não definir `OXIDE_DISPOSABLE_VM=confirmed` no host. Preservar as guardas atuais
do 016 e a confirmação explícita do participante dentro da VM. A variável de
confirmação é um reconhecimento humano, não detecção nem barreira de segurança.
Compilação no host continua permitida, sem executar os binários resultantes.
O fluxo manual já documentado dentro de uma VM permanece disponível.

O construtor escolherá distribuição, versões exatas, transporte de arquivos e
limites de recursos após verificar disponibilidade e compatibilidade. Não é
necessário suporte a guest de outra arquitetura, GPU na VM ou execução de
binários externos arbitrários. Tempos, endereços e PIDs não são reproduzíveis
byte a byte; o objetivo é repetir condições e resultados funcionais.

## Distribuição e documentação

O validador local `scripts/validate.py` hoje exclui Makefile na raiz do pacote.
Atualizar essa lista e seus testes. Novos formatos de ambiente devem ser
enumerados explicitamente; não liberar extensões ou caminhos indiscriminadamente.

O empacotador real pertence ao website, disponível no checkout irmão
`../oxideclub.dev`. Sua lista está em `src/lib/lab-files.mjs`, com testes em
`tests/lab-files.test.mjs`; ela também exclui Makefile na raiz. A implementação
inclui uma alteração coordenada nessa lista e testes do pacote real. Escrita no
checkout irmão depende das permissões do ambiente. Caso essa escrita não seja
possível, registrar a integração como pendente e entregar o patch necessário;
não declarar downloads funcionais.
Mudanças locais neste repositório não publicam o site automaticamente.

Atualizar README de cada laboratório, README principal, CONTRIBUTING e template
para novas atividades. Documentar requisitos do GNU Make e shell POSIX. Recursos
auxiliares necessários ao pacote devem estar dentro de sua árvore distribuída.

## Validação e critérios de conclusão

1. Os 18 laboratórios oferecem a interface, com ajuda correta e falhas explícitas.
2. Validar primeiro 007, 003 e 016; depois expandir aos demais sem alterar contratos.
3. Exercitar comandos em cópias isoladas dos arquivos distribuídos, fora do repo.
4. Confirmar que `test` preserva rejeições dos starters e sucessos dos materiais
   completos. Não corrigir starters para obter CI verde.
5. Verificar recompilação quando um fonte muda nos builds incrementais existentes.
6. Confirmar que `clean` preserva relatos, evidências e arquivos do participante.
7. Testar seletores inválidos, dependências ausentes e recusa de execução do 016
   sem confirmação. Não executar seus binários no host para testar recusas.
8. Validar boot, preparação, sanitizers, guardas, coleta de resultados e descarte
   da VM com os materiais previstos. Falta de QEMU, imagem ou permissão é uma
   limitação registrada, não validação bem-sucedida.
9. Rodar os checks editoriais e de preparação afetados, respeitando requisitos
   de hardware e isolamento. Não exigir CUDA para aprovar o restante do repositório.

## Fora do escopo

Soluções dos exercícios, renomeação estrutural dos materiais existentes,
instalação global automática, suporte Windows nativo, publicação do website e
conversão de todos os laboratórios para containers ou VMs.
