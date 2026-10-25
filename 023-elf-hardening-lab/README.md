# Guia local — Evidências de hardening em executáveis ELF

Leia o [enunciado](index.md). O laboratório está aprovado para publicação, com `draft: false`.

## Ambiente

Linux x86-64, GCC, GNU binutils, glibc e Python 3.10 ou posterior. A coleta exige `/proc/self/maps`.
Validação: GCC 16.2.1, binutils 2.47, glibc 2.44, Python 3.14.8, kernel 7.2.8-9-omarchy.
Essas versões descrevem o ambiente observado; outras versões exigem nova inspeção.
Não há downloads nem dependências Python externas.

## Preparar e executar

A interface Make oferece `make help`, `make setup`, `make build`, `make test`,
`make run`, `make clean` e `make verify-preparation`. O alvo padrão mostra a ajuda.
`run` guarda as evidências em uma pasta nova de `results/`; `clean` preserva essas evidências.
`verify-preparation` verifica o starter original; após editar, use `make test`.
`make run` constrói, verifica e coleta os seis perfis em uma pasta nova de evidências.

A partir deste diretório, use um diretório de saída novo:

```sh
python3 experiments/run.py build --out /tmp/oxide-023-run
python3 checks/check.py --out /tmp/oxide-023-run
python3 experiments/run.py collect --out /tmp/oxide-023-run
```

O build usa a mesma sonda nos seis perfis do contrato. `commands.txt` registra cada comando completo.
A coleta executa `readelf` e `objdump`, preserva seis mapas e lança A/B vinte vezes cada.
Cada lançamento usa um novo executável via `subprocess`, fora do debugger. Não altera ASLR nem políticas do host.
`environment.json` registra versões, kernel, política legível e variáveis `LD_*`/`GLIBC_*`.
A chamada `dlopen` usa `RTLD_NOW` para obter uma referência da libc; isso não equivale a pedir `BIND_NOW` para o executável.

Saídas: `A.elf.txt` a `F.elf.txt`, `A.asm.txt` a `F.asm.txt`, mapas completos,
`samples.json`, tabela `samples.csv` e hashes dos binários. O JSON preserva endereço da referência, intervalo, permissões e caminho.
Para o executável e a biblioteca, `base` é o menor início dos mapas daquele arquivo; `BIAS` é o deslocamento do loader.
Para stack e região anônima, a tabela usa o início do mapa que contém a referência registrada.
Falhas encerram o comando com status diferente de zero. Logs parciais não contam como coleta completa.

## Verificar

O check deve terminar com status zero: 18 casos funcionais, seis rejeições de limite e cinco controles negativos.
Os resultados normativos são `sum=0`, `sum=65` e `sum=505`, cada um seguido por LF.
Os controles negativos removem ou corrompem dados de identidade; devem falhar pelo motivo exibido.
Uma ferramenta ausente, timeout ou `/proc` indisponível é erro de preparação, não propriedade do executável.

Este laboratório é de observação. Não há implementação defeituosa para corrigir nem teste que aprove o relato.
A tarefa incompleta é a [matriz](materials/matrix.md): faça previsões, anote o disassembly e interprete as evidências.
O check não decide presença, alcance ou eficácia das mitigações. Não use endereços desta validação como resultado esperado universal.

## Registrar

Use o [modelo de relato](report-template.md). Entregue a matriz, a tabela das quarenta execuções e as evidências vinculadas.
Complete os três estados previstos no contrato. Conte valores distintos por região sem estimar entropia.
Inspecione `reference_sum` em A/C e relacione `RELRO`, `BIAS`, program headers e mapas de D/E/F.
Os intervalos `RELRO` são endereços runtime, com fim exclusivo. Considere o tamanho de página registrado ao comparar proteções.

Estimativa provisória: 10–16 horas. Recalibre-a no piloto coordenado pelo clube.

## Licenças

Código original: MIT, conforme [aviso](materials/LICENSE.md). Documentação: CC BY 4.0. Dados originais: CC0 1.0.
Origem curricular: atividade 35 do caderno de 25/10/2026. Revisão do pacote: `023-preparacao-1`.
