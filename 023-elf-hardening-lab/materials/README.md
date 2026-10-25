# Materiais — Evidências de hardening em executáveis ELF

**Situação:** materiais aprovados para publicação.

## Inventário

- [c/probe.c](c/probe.c): sonda benigna, função `reference_sum`, chamada externa `strlen` e mapas próprios.
- [matrix.md](matrix.md): matriz vazia para hipóteses, resultados e limites.
- [LICENSE.md](LICENSE.md): licença MIT dos fontes originais.
- [../experiments/run.py](../experiments/run.py): seis builds, inspeção ELF/disassembly e coleta de quarenta lançamentos.
- [../checks/check.py](../checks/check.py): casos funcionais independentes e controles negativos de identidade da coleta.

## Interface da sonda

`probe TEXTO` aceita zero a 63 bytes, exceto o argumento reservado `--maps`. Imprime a soma dos bytes sem sinal.
Casos normativos: texto vazio → `sum=0`; `A` → `sum=65`; `Oxide` → `sum=505`. Todos terminam com LF e status zero.
Argumentos ausentes, extras ou texto maior que 63 bytes retornam 2. Não há entradas que exijam corrupção de memória.

`probe --maps` retorna 0 após a coleta e 3 quando uma operação necessária falha.
A saída contém PID, tamanho da página, quatro referências `ANCHOR`, biblioteca resolvida, `BIAS`, eventual intervalo `RELRO` e `MAPS`.
Após `MAPS`, preserva as linhas de `/proc/self/maps`.

A referência do executável aponta para `reference_sum`; a da stack aponta para uma variável local viva.
A biblioteca é `libc.so.6`, resolvida por `dlsym` e identificada também por `dladdr`.
A região anônima pertence a um `mmap` próprio de três páginas. Só a página central recebe leitura/escrita;
as duas páginas laterais permanecem sem acesso. A referência aponta para essa página central enquanto ela está mapeada.
Nenhum endereço é presumido. Falta de correspondência impede aceitar a amostra.

## Responsabilidade do participante

Registre previsões antes da coleta. Preencha a matriz e explique cada mecanismo com evidências próprias.
A sonda e os scripts são instrumentos, não uma solução do relatório. O array local `volatile` e `noinline`
preservam o objeto de inspeção; somente o código emitido permite concluir como foi instrumentado.
Confira carregamento, armazenamento, comparação do guard e caminho de falha sem provocar overflow.

Os comandos e resultados da preparação estão no [guia local](../README.md).
Não acrescente flags aos perfis sem identificar uma experiência separada. Não modifique políticas globais.

## Origem e licenças

Fontes e instrumentos escritos para o Oxide Club em 2026, sem código de terceiros incorporado: MIT.
Documentação original: CC BY 4.0; dados originais: CC0 1.0. Revisão `023-preparacao-1`.
Especificação: atividade 35 do caderno de 25/10/2026; redação orientada por Português Técnico Claro 1.1.
