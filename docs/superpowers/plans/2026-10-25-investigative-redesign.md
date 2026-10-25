# Revisão investigativa Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Consolidar 004/009 e tornar 001/003 investigações práticas substantivas.

**Architecture:** Conteúdo e instrumentos em labs-analysis; consolidação editorial em challenges-revision; compatibilidade de rotas em site-labs-revision. Materiais históricos preservados e claramente opcionais ou arquivados.

**Tech Stack:** Markdown, C11, Python 3, Astro e testes Node.

**Spec:** ../specs/2026-10-25-investigative-redesign-design.md

## Global Constraints

- Preservar IDs e APIs dos desafios; não publicar nem enviar mensagens externas.
- Resultados de UB não são oráculos; indisponibilidade do sanitizador não conta como sucesso.
- Oito H2 dos laboratórios e pacotes autocontidos continuam válidos.
- Não exigir outra arquitetura para completar representação; explicitar limites do ambiente observado.

## Review Focus

- Destino consolidado precisa existir e não ser draft; testar no site.
- Links de downloads antigos precisam continuar acessíveis; verificar build local.
- Experimentos devem funcionar sem completar starters antigos; verificar preparação.
- ASan ausente ou sem diagnóstico esperado deve reprovar a coleta; validar runner.
- Não ler padding como dado semântico nem usar pointer após free no caso controle; revisar C e rodar sanitizadores.

## Tasks

- [x] 1. Consolidar orientação de 004/009 em challenges 017/021 e extensão 018, mantendo contratos. Validar com make check.
- [x] 2. Implementar supersededBy no site, testar filtro e destinos, preservar páginas de materiais, gerar build usando as worktrees.
- [x] 3. Acrescentar instrumentos e roteiros de 001/003, testar comportamento, atualizar README e preparação. Rodar unittest, validate e verify-preparation dos laboratórios alterados.
- [x] 4. Marcar 004/009 como consolidados em metadados, catálogo e documentação. Conferir diferenças e executar revisão independente do conjunto.

## Registro

Direção editorial aprovada pelo usuário em “Vamos prosseguir”. Execução sem nova rodada de aprovação para mudanças reversíveis. Alteração do site é necessária para tirar atividades das listagens sem quebrar acesso ao material histórico. Sem alteração do contrato dos desafios.

Verificação local: unittest 21/21; modelo de cache; preparação dos quatro IDs
17/17; estrutura 18 pacotes sem erros; modelos de relato consistentes.
Intervenções privadas executadas: quarta word, marker e contraexemplo de round-trip
em O0/O2 sob UBSan; mutação após cópia e rejeição de geração sob ASan/LSan.
Revisão independente sem achados acionáveis. O teste de memória falha corretamente
quando LSan não consegue operar sob ptrace; a execução fora do sandbox passou.
Challenges: make check aprovado; contratos e vetores preservados.
Site: 142 testes, integração e Astro check sem erros; build final aprovado com 49 páginas, 16 laboratórios ativos e dois históricos.
Assets e ZIPs novos/históricos conferidos contra os fontes. Avisos do build:
coleções locais de notas/reuniões vazias; nenhuma falha de conteúdo dos laboratórios.
Decisão: o build integrado usa overlay temporário com taxonomia existente do site,
pois a branch local de challenges ainda não contém areas.json/area. Não se altera
a branch original nem se enfraquece o schema. A integração deve incluir a taxonomia
antes de publicar essa branch de challenges. Nenhum deploy, push ou merge executado.

Integração posterior concluída a pedido do usuário: taxonomia de áreas incorporada
a challenges-revision a partir do commit 28f2617, preservando a consolidação.
Registro com seis áreas e 21 referências validado por make check (41 testes Python
e suítes Rust). Build direto das worktrees aprovado: 49 páginas, sem overlay.
A dependência de taxonomia descrita acima está resolvida. Avisos restantes somente
sobre coleções locais vazias de notas/reuniões. Sem publicação ou commits.
