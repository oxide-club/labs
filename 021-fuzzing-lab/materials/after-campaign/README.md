# Após a campanha — kit de apoio OXF1

Este kit é público e acompanha o laboratório. Recomenda-se consultá-lo depois de registrar a campanha inicial: ele revela entradas e mecanismos dos dois defeitos preparados. Essa sequência é pedagógica, não uma restrição de acesso.

Se consultar o kit antes da campanha, registre essa condição no relato. Uma entrada obtida daqui tem origem **fornecida pelo clube**, mesmo quando você a executa no motor de fuzzing. Não a contabilize como descoberta espontânea. O uso de apoio não impede concluir a investigação.

## Conteúdo e versão

- [Reproducers](reproducers.json): duas entradas em hexadecimal, seus hashes SHA-256 e o hash do parser inicial correspondente.
- [Regressões completas](regression.py): 125 casos derivados do contrato e cinco chamadas intercaladas.
- Este guia: comandos, resultados esperados e critérios para identificar os defeitos.

Os arquivos foram preparados pelo clube. O kit não inclui solução corrigida, mutantes ou logs históricos. Dados originais: CC0 1.0; script: MIT; documentação: CC BY 4.0.

Antes de modificar o parser, confira seu hash com o campo `parser_sha256`. Uma atualização do starter exige revalidar o kit. Diferenças de hash após sua correção são esperadas.

## Materializar as entradas

Execute a partir da raiz do laboratório:

```sh
python3 - <<'PYTHON'
from pathlib import Path
import hashlib
import json
kit = json.loads(Path("materials/after-campaign/reproducers.json").read_text())
out = Path("work/support")
out.mkdir(parents=True, exist_ok=True)
for item in kit["reproducers"]:
    data = bytes.fromhex(item["hex"])
    assert hashlib.sha256(data).hexdigest() == item["sha256"]
    (out / (item["id"] + ".bin")).write_bytes(data)
    (out / (item["id"] + ".hex")).write_text(data.hex() + "\n")
PYTHON
```

Os arquivos `.bin` servem como entradas binárias. Os arquivos `.hex` usam o transporte do runner determinístico. Não inclua essas reservas no corpus inicial de uma campanha que pretende registrar como descoberta independente.

## Reproduzir e interpretar

Compile o runner pelo [guia local](../../README.md). Execute os casos separadamente:

```sh
ASAN_OPTIONS=detect_leaks=1:abort_on_error=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 materials/starter/c/build/runner < work/support/reserve-a.hex
ASAN_OPTIONS=detect_leaks=1:abort_on_error=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 materials/starter/c/build/runner < work/support/reserve-b.hex
```

Se LeakSanitizer não inicializar no ambiente, siga o procedimento do guia local e registre a limitação. Uma falha de inicialização não confirma o defeito.

### Reserva A — acesso fora do buffer

A entrada declara um registro numérico de dois bytes, mas fornece apenas um. No starter identificado pelo manifesto, a leitura por `le16` ocorre antes da validação da disponibilidade dos dados. O runner aloca um buffer com o comprimento exato; ASan deve identificar uma leitura além desse buffer.

Depois da correção, a entrada deve retornar `Truncated`, sem diagnóstico de acesso inválido. Não exija uma linha de fonte ou endereço fixo no diagnóstico. Uma saída não zero, isoladamente, não comprova a causa.

Compare entradas com dados ausentes, completos e comprimento declarado inválido. Na minimização, preserve a identidade do defeito: obter apenas uma rejeição legítima do cabeçalho não atende a esse objetivo. Esta reserva não vem acompanhada de garantia de minimalidade global.

### Reserva B — soma truncada

A entrada contém dois valores numéricos de 40000. A soma contratada em `u32` é 80000. O starter reduz o acumulador a 16 bits e produz 14464. Essa conversão pode não gerar diagnóstico de ASan ou UBSan; o defeito é a divergência do contrato.

Após a correção, o runner deve produzir:

```text
Ok 0 80000 2 1:409c 1:409c
```

Confira também um registro, somas 65535 e 65536 e a soma de dezesseis valores 65535. Explique a invariante e acrescente regressões próprias.

## Verificar após as correções

```sh
python3 materials/after-campaign/regression.py materials/starter/c/build/runner
```

No starter, a suíte deve detectar os defeitos. Após uma correção conforme ao contrato, deve retornar zero e informar `cases=125 interleaved=5 failures=0`. Violações isoladas exigem erro específico; violações coexistentes aceitam os erros aplicáveis previstos pelo oráculo.

O participante ainda deve implementar o fuzz target, reproduzir e explicar os dois defeitos, minimizar pelo menos um caso e justificar as correções. A suíte fornecida não substitui essas entregas.
