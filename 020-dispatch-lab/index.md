---
title: "Laboratório de Monomorfização e dynamic dispatch"
area: "compilation-execution"
slug: "020-dispatch-lab"
summary: "Compare generics, trait objects e enum com trabalho equivalente, disassembly e medições."
question: "Como a seleção de comportamento aparece no código gerado e em medições comparáveis?"
draft: false
publishedAt: 2026-10-25
topics: ["Monomorfização", "Dynamic dispatch", "Desempenho"]
prerequisites: ["Traits e generics", "Trait objects", "Disassembly", "Medição de desempenho"]
tools: ["Cargo", "nm", "objdump"]
environment: "Linux x86-64; Rust/Cargo 1.98.1, GNU binutils e harness fornecido"
difficulty: intermediate
---

## O que vamos investigar

Investigue como a seleção de comportamento por generics, `&dyn Op` e `enum` aparece no código gerado e em medições comparáveis. Defina `Op::apply(&self, x: u64) -> u64` e dois comportamentos: `Add { delta }` e `Mul { factor }`. Produza os três processadores e confirme resultados iguais para cada comportamento antes de medir.

Preveja a presença de especializações, chamadas diretas ou indiretas nos builds sem e com otimização. Depois confronte essas previsões com símbolos, disassembly e medições do mesmo workload. O objetivo é explicar as formas de dispatch efetivamente observadas e os limites da comparação, sem exigir uma variante vencedora.

### Por que investigar este mecanismo

Generics permitem especialização por tipos concretos; trait objects permitem seleção de métodos através de uma interface dinâmica. Essas propriedades orientam a compilação, mas o resultado final também depende de inlining, eliminação de código e outras otimizações. Um programa com `dyn Trait` pode perder uma chamada indireta quando o compilador descobre o tipo concreto. A investigação deve comparar o que o código-fonte permite com o que o build efetivamente contém. [R27.1](https://doc.rust-lang.org/reference/types/trait-object.html), [R27.2](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html).

O exercício também ensina a reconhecer uma comparação injusta: mudar simultaneamente dispatch, organização dos dados, alocação e sequência de operações impede atribuir uma diferença de tempo a uma causa única.

### Objetivos de aprendizagem

- Implementar static dispatch, dynamic dispatch e seleção por `enum` com a mesma semântica, para sustentar uma comparação controlada.
- Formular previsões sobre especializações e chamadas diretas ou indiretas e confrontá-las com os artefatos dos builds.
- Detectar devirtualização e inlining como possíveis explicações para resultados semelhantes.
- Produzir medições com trabalho equivalente, resultado consumido e condições registradas.
- Separar observações de símbolos, assembly e desempenho das inferências usadas para explicá-las.
- Separar garantias da linguagem de decisões específicas do compilador e do target.

### Conceitos trabalhados

Monomorfização; vtables; chamadas indiretas; inlining; devirtualização; equivalência de workloads; consumo de resultados; medição e dispersão; tamanho de código; evidência versus inferência.

### Contrato técnico

Os três processadores recebem a mesma sequência de `u64`, aplicam **uma única operação homogênea** a cada elemento na mesma ordem e devolvem a soma modular dos resultados. Soma, multiplicação e checksum usam explicitamente aritmética `wrapping`, sem diferença entre debug e release. Há duas campanhas independentes: `Add { delta: 7 }` e `Mul { factor: 3 }`.

O processador genérico recebe `&T` com `T: Op`; o dinâmico, `&dyn Op`; o terceiro recebe referência a um `enum` com os mesmos parâmetros. Os objetos são preparados antes da região medida. O núcleo não compara generic homogêneo com coleção dinâmica heterogênea. Alocação, parsing, impressão e geração de dados ficam fora da medição; a construção das abstrações não será contabilizada como custo de chamada.

Os builds de inspeção usam níveis de otimização 0 e 3, mantendo target, política de panic e símbolos de diagnóstico iguais. LTO fica desativado no núcleo e a configuração de codegen units é comum às variantes. Registre compiler, flags, CPU, tamanho dos dados e número de repetições; não altere `target-cpu` entre concorrentes.

O harness precisa consumir o checksum e dificultar a propagação de entradas constantes, usando `black_box` de forma documentada. Essa função é uma barreira de otimização por melhor esforço, não uma garantia universal de forma do assembly. [R27.3](https://doc.rust-lang.org/std/hint/fn.black_box.html). Sempre confira o trabalho remanescente no código gerado.

Não se exige chamada indireta em todo build com `dyn`. Se ela desaparecer, a entrega deve localizar a evidência e discutir devirtualização, inlining ou eliminação de código. O layout observado de vtable ou de trait object não será declarado ABI estável nem usado via `transmute`.

## Antes de começar

Traits, generics, `dyn Trait`, enums, slices e ownership; noção de otimização e linking; leitura elementar de disassembly, chamadas e registradores. Atividades de compilação, engenharia reversa e ABI são preparações recomendadas. Conhecer o funcionamento interno do LLVM não é requisito.

### Linguagens e ambiente

Linux x86-64; Rust/Cargo 1.98.1, GNU binutils e harness fornecido.

Rust faz parte do mecanismo investigado e é obrigatório no núcleo.

**Aprovado para publicação.** O [guia local](README.md) descreve os materiais, comandos e limites de execução.

## Materiais

Leia o [guia dos materiais](materials/README.md). Use o [modelo de relato](report-template.md) para registrar a investigação. O guia identifica os instrumentos fornecidos e as partes que o participante deve implementar.

O pacote fornece assinaturas, loader, gerador de dataset, harness, scripts de build/inspeção e registro de ambiente. As fixtures pequenas têm resultados independentes. O participante implementa os processadores e produz suas próprias medições.

## Etapas da investigação

Registre previsões antes de executar. Preserve entradas, comandos e resultados para explicar o mecanismo e os limites de cada conclusão.

### Prever

Antes de compilar os builds de inspeção e medir, registre previsões verificáveis para cada campanha e nível de otimização:

- **Equivalência semântica:** os três processadores devem produzir o mesmo checksum, inclusive com overflow modular, porque recebem os mesmos valores e aplicam a mesma operação homogênea.
- **Especialização:** o uso de tipos concretos no processador genérico permite instâncias especializadas. Preveja onde procurá-las, sem fixar uma quantidade de símbolos: otimizações e eliminação de funções podem mudar sua representação final.
- **Dispatch observado:** o uso de `&dyn Op` permite chamadas via interface dinâmica, mas não garante uma chamada indireta em todo build. O conhecimento do tipo concreto pode permitir devirtualização, inlining ou eliminação; a hipótese deve ser confrontada com o local de chamada e o trabalho remanescente.
- **Medição:** a organização das chamadas pode produzir diferenças de tempo e de tamanho de código, mas seu sinal e magnitude dependem do build, do workload e do ambiente. Tempos próximos, invertidos ou ruidosos são admissíveis; não há razão fixa de velocidade prevista pelo contrato.

Mantenha a previsão anterior ao experimento separada do resultado obtido e da explicação proposta depois da inspeção.

### Conduzir os experimentos

1. Calcule os resultados de uma fixture pequena, incluindo overflow modular, e registre as previsões sobre equivalência, especialização e dispatch.
2. Implemente as variantes e confirme equivalência antes de ativar medições. Verifique que objetos e dados estão preparados fora da região medida.
3. Compare símbolos e locais de chamada nos níveis de otimização 0 e 3; anote também funções que desapareceram e o trabalho que continua presente no código gerado.
4. Use a separação de módulos/crates prevista pelo starter para investigar o efeito de conhecer o tipo concreto. A separação ajuda a estruturar o experimento, sem prometer impedir toda otimização.
5. Meça repetições do mesmo workload, guarde os dados brutos e relate dispersão. Discuta custo por elemento e tamanho do código sem exigir um vencedor.
6. Leia o tratamento de chamadas virtuais no codegen e relacione-o ao artefato observado. [R27.4](https://github.com/rust-lang/rust/blob/1.98.1/compiler/rustc_codegen_ssa/src/mir/block.rs).
7. Confronte as previsões com as evidências e registre as condições que permitem, ou impedem, atribuir uma diferença ao dispatch.

### Registrar as evidências

Entregue código; testes de equivalência; comandos reproduzíveis; trechos pequenos de disassembly anotados; métricas brutas e síntese; relatório com conclusões restritas ao build e workload estudados. Cada conclusão sobre desempenho deve informar a condição experimental que a sustenta.

Preencha a matriz de evidências para as campanhas `Add { delta: 7 }` e `Mul { factor: 3 }`, mantendo os campos de previsão e observação separados:

| Questão | Previsão a registrar | Evidência e observação a produzir | Limite a declarar |
| --- | --- | --- | --- |
| Equivalência | Mesmo checksum para as três variantes. | Resultados das fixtures e do dataset carregado em runtime. | Equivalência vale para o trabalho e o contrato verificados. |
| Especialização e dispatch | Forma esperada das chamadas nos níveis 0 e 3. | Símbolos e locais de chamada anotados, inclusive ausências por otimização. | Ausência de um símbolo isolado não identifica, sozinha, qual otimização ocorreu. |
| Conhecimento do tipo concreto | Possível efeito da separação de módulos/crates. | Diferenças observadas entre os builds previstos pelo starter. | A separação não garante impedir devirtualização ou inlining. |
| Tempo e tamanho de código | Hipótese contextual, sem vencedor obrigatório. | Dados brutos, dispersão, custo por elemento e medidas do artefato. | CPU, flags, entrada, repetições e trabalho remanescente restringem a conclusão. |

Documente o uso de `black_box` e o exame do assembly que confirma o trabalho efetivamente medido.

### Explicar e delimitar

Distingua a evidência diretamente observada — como uma chamada indireta em um local identificado, um trecho incorporado ao chamador ou os tempos registrados — da inferência sobre a transformação do compilador. Se a chamada virtual desaparecer, localize a evidência e discuta devirtualização, inlining ou eliminação de código, sem apresentar o nome da abstração no fonte como prova do assembly final.

Explique resultados próximos, invertidos ou ruidosos com as condições registradas e a dispersão disponível. Alterar simultaneamente dispatch, layout, alocação ou sequência de operações impede atribuir o efeito a uma única causa. `black_box` atua por melhor esforço, e o layout observado de trait objects ou vtables não constitui ABI estável. As conclusões se restringem aos builds e workloads estudados; não autorizam afirmar que uma forma de dispatch será sempre mais rápida.

## Critérios de conclusão

Entrada vazia produz checksum zero. Para `[0, 1, 2, u64::MAX]`, a campanha Add produz checksum `30`; a campanha Mul produz `6`, por aritmética modular. Todas as variantes devem concordar também para dados com valores repetidos e um dataset maior carregado em runtime.

A avaliação deve confirmar que os mesmos valores, operação e quantidade de elementos foram processados. O relatório precisa distinguir pelo menos uma evidência de especialização e a situação de dispatch observada, inclusive quando uma chamada virtual foi otimizada. Tempos próximos, invertidos ou ruidosos são resultados admissíveis se explicados; não se exige uma razão fixa de velocidade ou quantidade fixa de símbolos.

Uma previsão refutada pode ser um resultado válido. Erro de preparação, instrumento incorreto ou timeout não classificado não responde à pergunta experimental. Registre requisitos bloqueados e repita-os em ambiente compatível antes de concluir o núcleo.

## Extensões opcionais

Compare LTO, diferentes tamanhos de operação e custos de construção. Em uma extensão heterogênea, compare `dyn` e `enum` com a mesma sequência explícita de operações, registrando diferenças de layout e indireção de dados. Não generalize um microbenchmark para “Rust genérico sempre é mais rápido”.

## Participação no clube

Compartilhe código e relato em seu próprio repositório. Apresente a pergunta, a previsão inicial, uma entrada pequena, os comandos e as evidências na conversa do clube. Você pode compartilhar uma tentativa incompleta; identifique o que ainda não foi executado ou explicado.

Use o [modelo de relato](report-template.md). Preserve o limite de páginas indicado nos entregáveis, quando houver; mantenha código, logs e dados extensos em arquivos próprios.

## Referências e atividades relacionadas

As [leituras orientadas](references.md) indicam documentação e código real. Relacione a investigação aos conhecimentos prévios e às atividades citadas, sem tratá-las como uma sequência obrigatória. Os IDs em prosa identificam atividades do catálogo; propostas em elaboração não equivalem a materiais já publicados.
