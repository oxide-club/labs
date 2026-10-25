---
title: "Laboratório de Evidências de hardening em executáveis ELF"
area: "compilation-execution"
slug: "023-elf-hardening-lab"
summary: "Relacione seis builds ELF a instruções, metadados e evidências de hardening em execução."
question: "Que evidência permite afirmar a presença e o alcance de uma mitigação num executável específico?"
draft: true
topics: ["ELF", "Hardening", "Código gerado"]
prerequisites: ["ELF", "Linking dinâmico", "Disassembly", "Mapeamentos de memória"]
tools: ["GCC", "GNU binutils", "/proc"]
environment: "Linux x86-64; C, GCC, GNU binutils e glibc; versões a registrar"
difficulty: advanced
---

## O que vamos investigar

Investigue que evidência permite afirmar a presença e o alcance de uma mitigação num executável específico. Construa seis variantes do programa benigno do clube, formule previsões para as comparações e preencha uma matriz mecanismo → camada → evidência → propriedade → limitação. Todas devem produzir o mesmo resultado para entradas válidas.

A fixture terá função identificável para inspeção de canary, chamada externa e relatório de mapeamentos próprios. Explique a verificação pelas instruções emitidas; nenhuma entrada exigirá overflow, acesso fora de limites ou execução de dados. Os builds e scripts são instrumentos do experimento; a conclusão exige interpretar metadados, instruções e observações em execução, inclusive quando contrariarem a previsão.

### Por que investigar este mecanismo

Uma lista de flags não demonstra o comportamento do artefato. Defaults da distribuição, otimização, loader e kernel afetam o resultado. Este laboratório relaciona configuração, código gerado, metadados ELF e observação em execução.

Canaries, PIE, ASLR, NX e RELRO ocupam camadas diferentes. O [manual do GCC](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html) explica a instrumentação de funções; o [manual do linker](https://sourceware.org/binutils/docs/ld/Options.html) descreve requisitos registrados no ELF; e a [documentação do kernel](https://docs.kernel.org/admin-guide/sysctl/kernel.html#randomize-va-space) descreve políticas de randomização. O participante deverá organizar essas relações, preservando a diferença entre presença de um mecanismo e ausência de defeitos.

### Objetivos de aprendizagem

- Produzir e identificar seis configurações com comandos de build reproduzíveis.
- Localizar evidências de canary numa função concreta e explicar o caminho de verificação.
- Distinguir executável PIE, randomização observada e política do ambiente.
- Correlacionar requisitos de stack e segmentos com permissões de mapeamento.
- Diferenciar ausência de RELRO, RELRO parcial e RELRO acompanhado de resolução antecipada.
- Redigir conclusões limitadas pela evidência, sem converter um indicador de hardening em garantia de segurança.
- Formular e confrontar hipóteses sobre diferenças entre builds, separando a configuração solicitada do mecanismo efetivamente observado.

### Conceitos trabalhados

Compilador, linker, loader, kernel e metodologia de comparação. O foco será rastrear cada afirmação até instruções, program headers, dynamic tags, intervalos de memória ou amostras. O relatório também trabalhará fatores de confusão, como otimizações e defaults da toolchain.

### Contrato técnico

Mantenha fonte e toolchain iguais. Use `-O1 -g -fno-lto` em todos os builds e `-Wl,-z,noexecstack` em todo linking. Acrescente os flags de cada perfil; registre os comandos completos.

| Perfil | Compilação | Linking pelo driver GCC |
|---|---|---|
| A: referência | `-fno-pie -fno-stack-protector` | `-no-pie -Wl,-z,norelro,-z,lazy` |
| B: PIE | `-fPIE -fno-stack-protector` | `-pie -Wl,-z,norelro,-z,lazy` |
| C: canary | `-fno-pie -fstack-protector-all` | `-no-pie -Wl,-z,norelro,-z,lazy` |
| D: RELRO parcial | `-fno-pie -fno-stack-protector` | `-no-pie -Wl,-z,relro,-z,lazy` |
| E: RELRO e resolução antecipada | `-fno-pie -fno-stack-protector` | `-no-pie -Wl,-z,relro,-z,now` |
| F: combinação | `-fPIE -fstack-protector-all` | `-pie -Wl,-z,relro,-z,now` |

A evidência do artefato e da execução prevalece sobre o nome do perfil. Registre proteções adicionais e variáveis relevantes do loader; não descreva A como “sem segurança”.

Para C, escolha uma opção que instrumente a função de referência de forma verificável, como `-fstack-protector-all`, e confirme o resultado no disassembly. Identifique carga do guard, armazenamento, comparação e caminho de falha. A presença isolada de `__stack_chk_fail` na tabela de símbolos não basta para demonstrar proteção daquela função. Chamar essa função diretamente tampouco demonstra que o compilador detectou corrupção.

Colete ELF header, program headers, dynamic tags e disassembly relevante. Identifique PIE pelo conjunto de evidências do executável produzido; não classifique qualquer `ET_DYN` isolado como programa PIE. Para NX, relacione `PT_GNU_STACK`, flags dos segmentos carregáveis e mapas da execução. Uma stack sem `x` não autoriza concluir que nenhuma página do processo possa executar.

Para RELRO, localize `PT_GNU_RELRO`, a presença ou ausência de resolução antecipada e o intervalo correspondente após o carregamento. Diferencie os metadados do arquivo e a proteção aplicada pelo loader. A documentação do [GNU ld](https://sourceware.org/binutils/docs/ld/Options.html) define o pedido de proteção pós-relocation e o efeito de `now`; a confirmação de runtime deve aparecer separadamente.

Execute A e B em vinte lançamentos novos cada, fora do debugger, usando `exec` de cada variante. Registre base do executável, stack, biblioteca selecionada e região anônima própria, identificando inequivocamente cada região. Repetir somente `fork` não atende ao objetivo. Registre a política `randomize_va_space` quando legível, sem alterar `sysctl`, personalidade do processo ou configuração global.

A saída será uma tabela por variante e uma tabela das quarenta execuções. Cada conclusão receberá um estado: `confirmado pela evidência`, `ausente na evidência coletada` ou `inconclusivo`, acompanhado da evidência específica. Falhas de build, ferramenta indisponível e execuções incompletas serão explícitas; não completar células com valores presumidos.

## Antes de começar

ELF, seções/segmentos, stack frames, relocations, linking dinâmico e disassembly x86-64. Saber usar `readelf`, `objdump` e mapas do próprio processo. Recomenda-se o laboratório `022-page-protection-lab`; exploração não é pré-requisito.

### Linguagens e ambiente

Linux x86-64; C, GCC, GNU binutils e glibc; versões a registrar.

C é a linguagem-base do núcleo. As alternativas indicadas nas extensões são complementares.

**Em elaboração.** Os instrumentos foram preparados e verificados em Linux x86-64. O [guia local](README.md) contém os comandos. Revisão independente e piloto continuam pendentes.

## Materiais

Leia o [inventário dos materiais](materials/README.md). Execute a sonda e os instrumentos conforme o [guia local](README.md). Use o [modelo de relato](report-template.md) e a [matriz vazia](materials/matrix.md) para registrar a investigação.

Código-fonte pequeno e benigno, função de referência identificável e preservada na configuração indicada, entradas com resultados conhecidos, matriz vazia e configuração de toolchain suportada. A fixture deve evitar que a otimização elimine o objeto de estudo. Eventual animação ou programa artificial de “verificação de integridade” deverá vir rotulado como simulação; ele não conta como evidência de stack protector.

## Etapas da investigação

Registre previsões antes de executar. Preserve entradas, comandos e resultados para explicar o mecanismo e os limites de cada conclusão.

### Prever

Registre as previsões antes da coleta, indicando a comparação controlada, a camada envolvida e a evidência que poderá confirmar ou corrigir a hipótese.

| Hipótese verificável | Previsão e evidência |
|---|---|
| A/B diferem quanto à produção de um executável PIE. | A inspeção do executável produzido deve distinguir os perfis pelo conjunto de evidências, sem usar `ET_DYN` isoladamente. A previsão sobre variação de endereços será examinada separadamente nas vinte execuções novas de cada variante. |
| A/C diferem quanto à instrumentação da função de referência. | O disassembly de C deve permitir localizar carga, armazenamento e comparação do guard e caminho de falha, confrontados com A; a presença de um símbolo não basta. |
| A/D/E diferem quanto a RELRO e resolução antecipada. | Program headers e dynamic tags devem permitir separar os pedidos do linker; o mapeamento após o carregamento deve sustentar, separadamente, a conclusão sobre proteção aplicada. |
| O requisito de stack e as permissões observadas podem ser correlacionados. | `PT_GNU_STACK`, flags dos segmentos carregáveis e mapas da execução devem sustentar uma afirmação delimitada sobre as regiões identificadas, sem extrapolação para todas as páginas do processo. |
| As mudanças de configuração preservam o comportamento funcional benigno. | As seis variantes devem produzir os resultados conhecidos nos mesmos três casos válidos. |

Para A/B, antecipe quais regiões poderão variar e por quê, registrando a política do ambiente quando legível. A ausência de variação é um resultado a investigar. Não altere o ambiente para confirmar a previsão e não trate estas amostras como medida de entropia ou prova de eficácia de ASLR.

### Conduzir os experimentos

1. Liste a camada que deve mudar em cada comparação: A/B, A/C e A/D/E. Registre hipóteses e previsões, mantendo fonte e toolchain iguais e os comandos completos de cada perfil.
2. Construa as seis variantes, confira os três casos funcionais benignos e verifique se as flags solicitadas produziram os metadados e instruções esperados.
3. Anote o caminho de saída normal e o caminho de falha da função instrumentada, localizando carga, armazenamento e comparação do guard.
4. Relacione os intervalos ELF aos mapeamentos observados em execução. Separe a evidência presente no arquivo da proteção aplicada pelo loader.
5. Execute A e B em vinte lançamentos novos cada, por `exec`, fora do debugger. Registre inequivocamente as quatro regiões exigidas e resuma as amostras por região, indicando quantidade de valores distintos.
6. Confronte cada hipótese com a evidência e atribua um dos estados previstos no contrato. Investigue ausência de variação, proteções adicionais e resultados incompletos, sem presumir valores.
7. Explique dois resultados que não poderiam ser concluídos apenas pela linha de compilação e delimite cada conclusão por função, região, instante ou conjunto de amostras.

### Registrar as evidências

Scripts de build e coleta; identificação das seis variantes; saídas de inspeção; quarenta registros de execução; matriz de mecanismos e relatório de até quatro páginas. Acrescente uma anotação do disassembly da função escolhida e uma explicação de como o loader aplica uma das proteções observadas.

Inclua as hipóteses e previsões anteriores à coleta e sua comparação com os resultados. Cada afirmação da matriz deve apontar a evidência específica e sua limitação, separando metadados do arquivo, código gerado, proteção aplicada e comportamento amostrado.

### Explicar e delimitar

Uma conclusão sobre canary pertence à função cujo código foi inspecionado. Localizar `__stack_chk_fail` ou chamá-la diretamente não demonstra a instrumentação dessa função nem a detecção de corrupção pelo compilador. O laboratório observa o caminho gerado sem exigir corrupção deliberada.

PIE, política de ASLR e variação observada são afirmações distintas. As vinte amostras de A e as vinte de B permitem descrever os endereços registrados para as regiões identificadas; não estimam entropia, não comprovam eficácia de ASLR e não autorizam forçar variação por mudanças globais. Ausência de variação exige análise e registro, sem preencher lacunas com valores presumidos.

A observação de uma stack sem `x` limita-se àquela região e aos instantes de coleta; não significa que nenhuma página do processo possa executar. Para RELRO, diferencie o intervalo e a intenção registrados no ELF da proteção efetivamente aplicada pelo loader, e preserve a distinção entre RELRO parcial e resolução antecipada.

A combinação de mecanismos no perfil F não torna o artefato livre de defeitos. Defaults da toolchain, otimizações e variáveis do loader podem interferir na comparação. Por isso, cada conclusão deve usar os estados do contrato e declarar seu alcance por função, região, instante ou amostra; quando a coleta não sustentar a propriedade, registre a limitação ou a inconclusão.

## Critérios de conclusão

- As seis variantes passam pelos mesmos três casos funcionais benignos.
- A comparação A/C identifica a instrumentação da função escolhida, além de símbolos ou mensagens.
- A comparação A/D/E separa segmento RELRO e resolução antecipada.
- Todas as variantes têm seu requisito de stack e seu mapeamento observado registrados.
- A/B têm vinte amostras completas por variante; ausência de variação é investigada, sem manipular o ambiente para produzir o resultado desejado.
- O relatório não estima entropia nem comprova eficácia de ASLR a partir dessas amostras; identifica somente o comportamento observado.
- Toda propriedade tem uma limitação explícita, como alcance por função, região ou instante.

A conclusão exige explicar o mecanismo que liga cada comparação à propriedade alegada e registrar as hipóteses confirmadas, corrigidas ou inconclusivas. Nomes de perfis, flags, símbolos isolados e mensagens de uma simulação não substituem as evidências exigidas.

Uma previsão refutada pode ser um resultado válido. Erro de preparação, instrumento incorreto ou timeout não classificado não responde à pergunta experimental. Registre requisitos bloqueados e repita-os em ambiente compatível antes de concluir o núcleo.

## Extensões opcionais

Extensões: comparar GCC e Clang, CET disponível no ambiente ou um artefato Rust equivalente. Não se exigem exploits, bypasses, corrupção deliberada ou alteração de políticas do host. Mitigações não corrigem automaticamente o defeito que motivou sua existência. Conexões: laboratório `020-dispatch-lab` e laboratório `022-page-protection-lab`.

## Participação no clube

Compartilhe código e relato em seu próprio repositório. Apresente a pergunta, a previsão inicial, uma entrada pequena, os comandos e as evidências na conversa do clube. Você pode compartilhar uma tentativa incompleta; identifique o que ainda não foi executado ou explicado.

Use o [modelo de relato](report-template.md). Preserve o limite de páginas indicado nos entregáveis, quando houver; mantenha código, logs e dados extensos em arquivos próprios.

## Referências e atividades relacionadas

As [leituras orientadas](references.md) indicam documentação e código real. Relacione a investigação aos conhecimentos prévios e às atividades citadas, sem tratá-las como uma sequência obrigatória. Os IDs em prosa identificam atividades do catálogo; propostas em elaboração não equivalem a materiais já publicados.
