# Guia local — Fuzzing e análise de falhas

Leia o [enunciado](index.md). A variante C possui materiais executáveis validados. O laboratório permanece em elaboração, com `draft: true`; o piloto ainda não ocorreu.

## Ambiente

Linux x86-64, Clang com compiler-rt/libFuzzer, GNU Make e Python 3. Biblioteca padrão apenas; nenhuma instalação de dependências é necessária nos materiais. Ambiente observado: Clang 23.1.3. A variante Rust permanece aceita pelo contrato, mas não é fornecida neste pacote.

Estimativa provisória: 10–16 horas. Recalibre-a no piloto coordenado pelo clube. Execute em uma cópia gravável do pacote. Os comandos abaixo partem da raiz dessa cópia.

## Preparar e executar

```sh
clang --version
python3 --version
make -C materials/starter/c
python3 checks/check.py materials/starter/c/build/runner --smoke
python3 checks/test_phases.py
python3 checks/corpus.py work/corpus
```

O build e o smoke devem retornar zero. O smoke confere a preparação, sem aprovar o parser. Consulte o [inventário e a interface](materials/README.md).

Edite `materials/starter/c/fuzz_target.c`. Implemente o target antes de definir `PARTICIPANT_TARGET_READY` no fonte. A compilação de fuzzing falha deliberadamente enquanto essa tarefa estiver incompleta. Compare resultados válidos com expectativas independentes; uma rejeição legítima não deve provocar `abort`.

```sh
make -C materials/starter/c fuzz
python3 checks/campaign.py materials/starter/c/build/fuzz work/corpus work/session --seconds 600 --runs 1000000 --seed 21 --leaks on
```

O segundo comando só se aplica após implementar o target. Ele fixa um worker, `-max_len=4096`, `-timeout=2` e `-rss_limit_mb=512`. O RSS é fiscalizado periodicamente pelo motor, não constitui um limite instantâneo do kernel. O supervisor encerra o processo ao atingir o prazo de parede reservado.

Mantenha **o mesmo diretório `work/session` em todos os reinícios da campanha**, inclusive após corrigir o parser. Não apague `budget.json`. O supervisor reserva recursos antes de iniciar. Quando há uma estatística final única e válida de execuções, debita o consumo real e o tempo medido. Se faltam estatísticas confiáveis, conserva a reserva completa. Nunca ultrapassa 600 segundos ou um milhão de execuções, o primeiro limite alcançado.

Para continuar após preservar e classificar um artefato, repita o comando sem `--seconds` e `--runs`; ele usa o saldo restante. Pode escolher o corpus final da tentativa anterior como entrada. Não abra outra sessão para contornar o orçamento. Um lock impede campanhas simultâneas na mesma sessão.

Cada `attempt-*` conserva `corpus-start` (cópia inicial), `corpus` (mutável), log e artefatos. O manifesto registra hashes do corpus no início e no fim **da tentativa**, seed, target, opções, reserva e consumo. Estados distinguem conclusão, sinal, falha do motor, prazo externo e falha de lançamento. `signaled` inclui o nome do sinal; isso ainda exige classificar sua causa.

Para reproduzir fora do motor, converta um artefato para a entrada hexadecimal do runner:

```sh
python3 -c 'from pathlib import Path; print(Path("work/reproducer").read_bytes().hex())' > work/reproducer.hex
ASAN_OPTIONS=detect_leaks=1:abort_on_error=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 materials/starter/c/build/runner < work/reproducer.hex
```

`work/reproducer` é o arquivo preservado da sua investigação, não um arquivo distribuído. Para minimização, consulte as opções de libFuzzer nas [referências](references.md). Separe o orçamento de minimização do registro de descoberta e explique a identidade do defeito preservada.

## Verificar

Antes da campanha, `python3 checks/check.py materials/starter/c/build/runner` deve retornar zero no starter. Confere oito casos básicos, transporte e cinco chamadas intercaladas. `--smoke` é um alias do mesmo check. **Esse resultado não aprova o parser nem os critérios de conclusão.** Não inclui vetores reveladores nem diagnósticos dos defeitos preparados.

Após registrar a campanha, consulte o [kit público de apoio](materials/after-campaign/README.md). Ele contém os dois reproducers de reserva, explicações e a suíte completa. Registre esses materiais como fornecidos pelo clube, sem atribuir sua descoberta ao fuzzing. Se consultar o kit antes da campanha, registre essa condição. Execute:

```sh
python3 materials/after-campaign/regression.py materials/starter/c/build/runner
```

Esse check completo detecta os defeitos no starter; após as correções, exige 125 casos e cinco chamadas intercaladas aprovados. O oráculo calcula resultados de um modelo anterior à serialização. Violações isoladas exigem erro exato; quando há violações coexistentes, aceita os erros aplicáveis. Os critérios completos permanecem no enunciado. Acrescente suas próprias regressões e entradas vizinhas.

ASan e UBSan estão habilitados no Makefile. LSan fica ativo por padrão nos checks e na campanha (`--leaks on`). Na revisão, funcionou fora da sandbox com `ptrace_scope=1`: a referência passou e um controle com vazamento foi detectado. Dentro da sandbox, sua inicialização falhou. Não deduza disponibilidade apenas de `ptrace_scope`.

Se LSan não inicializar, registre contexto e mensagem; repita fora do debugger/sandbox quando autorizado. Uma execução com `ASAN_OPTIONS=detect_leaks=0:abort_on_error=1` nos checks ou `--leaks off` na campanha deve ser identificada como sem verificação dinâmica de vazamentos. ASan e UBSan continuam ativos. A aprovação de vazamentos no runner não aprova automaticamente o target que o participante construir.

Erro de compilador ou falha de inicialização é erro de preparação. Timeout ou saída não zero exige classificação; não conte automaticamente como um dos dois defeitos.

## Registrar

Use o [modelo de relato](report-template.md). Registre previsões, corpus, manifesto, comandos, sintomas, regressões e comparação antes/depois. Separe descoberta, reprodução e minimização; não some reproduções à estatística de descobertas. Para defeitos não descobertos, use os reproducers do kit público; identifique sua origem no relato. O kit permanece disponível após o piloto. Soluções completas não integram a distribuição.

A preparação passou por referência privada correta e seis mutantes distintos. Isso verifica os instrumentos nos casos executados, sem provar correção geral nem substituir a investigação do participante.

## Licenças

Código original: MIT, conforme [LICENSE.txt](materials/LICENSE.txt). Dados originais: CC0 1.0. Documentação original: CC BY 4.0. Origem e versão do pacote constam no [inventário](materials/README.md).
