# Guia local — Monomorfização e dynamic dispatch

Leia o [enunciado](index.md). O laboratório está aprovado para publicação, com `draft: false`.

## Ambiente

Validado em Linux x86-64, Rust/Cargo 1.98.1, LLVM 22.1.8 e Python 3.14.8.
Use GNU `nm`, `objdump` e `size` no PATH, junto à toolchain Rust.
O workspace não usa dependências externas.
Os perfis `inspect0` e `inspect3` usam otimização 0 e 3, respectivamente.
Ambos mantêm `debug=2`, `panic=unwind`, `lto=false` e `codegen-units=1`.
O coletor remove overrides do ambiente e usa um `CARGO_HOME` novo, sem configuração do usuário.
Recusa `.cargo/config` e `.cargo/config.toml` na pasta de trabalho e em qualquer ancestral.
Se encontrar um desses arquivos, encerra com status 2 antes do build; use outra pasta de saída.
Isso inclui `~/.cargo/config.toml` quando a pasta de trabalho está dentro de `$HOME`.
Nesse caso, use uma pasta própria fora de `$HOME`, por exemplo em `/tmp`, sem remover a configuração pessoal.
O `CARGO_HOME` isolado não desativa essa recusa preventiva dos ancestrais.
O coletor fixa `--target` no host informado por `rustc -vV` e usa diretório de build explícito.
Os perfis são fixados por `--config`; as flags críticas também usam `CARGO_ENCODED_RUSTFLAGS`.
Cada build usa uma área nova. O log `-vv` registra as invocações reais do `rustc`.
Antes de medir, o coletor confere otimização, LTO, codegen units, diagnóstico e panic nos dois crates.
Invocações ausentes ou flags divergentes interrompem a coleta. Os registros ficam em `*.rustc.json`.
Não altere `target-cpu` entre variantes.

## Preparar e executar

Execute a partir deste diretório:

```bash
python3 checks/test_support.py
python3 checks/check.py --build-only
python3 checks/check.py
```

Os dois primeiros comandos retornam 0. O último retorna 1 no starter, com `not yet implemented`.
Implemente os cinco corpos em `materials/starter/rust/core/src/lib.rs`.
Preserve as assinaturas públicas e use aritmética `wrapping` nas operações e no checksum.
Repita `python3 checks/check.py` e prossiga somente quando retornar 0.

Gere o dataset e execute a coleta após completar o starter:

```bash
python3 materials/generate.py --out /tmp/oxide-dispatch-data --n 65536
python3 experiments/collect.py --dataset /tmp/oxide-dispatch-data/dataset.txt --out /tmp/oxide-dispatch-run --repetitions 30
python3 experiments/summarize.py /tmp/oxide-dispatch-run/inspect3-separate.csv
```

Escolha diretórios novos para repetir os comandos; os instrumentos recusam sobrescrever a coleta.
O coletor aceita `--source CAMINHO` para uma cópia modificada do workspace.
Cada check e coleta restaura `Cargo.lock` de `Cargo.lock.txt` na área de execução.
Não é necessário copiar arquivos do checkout do autor.

## Medição e inspeção

O coletor testa antes de medir. Produz quatro builds: O0/O3, com core separado e no módulo local.
A feature `local-core` compila o mesmo fonte no crate do harness; não duplica a implementação.
O loader lê uma linha decimal `u64` por elemento, inclusive uma entrada vazia.
Os objetos, closures, dados e reserva de amostras são preparados antes da medição.
O harness usa uma chamada comum de closure por checksum; registre esse custo comum ao interpretar dados pequenos.

Cada combinação faz dois aquecimentos e trinta repetições por campanha/variante no comando acima.
A ordem das seis combinações gira a cada repetição. Add e Mul permanecem workloads homogêneos separados.
Cada tempo cobre uma passagem pela entrada. Impressão, parsing e validação ficam fora da região medida.
`black_box` recebe os dados, a referência concreta da operação e o resultado.
No caminho dinâmico, `black_box(&add) as &dyn Op` aplica a barreira antes da coerção.
Isso dificulta propagar os valores dos parâmetros sem esconder o tipo concreto e sua vtable.
Aplicar a barreira depois da coerção tornaria a vtable opaca e mudaria essa condição experimental.
O efeito de `black_box` continua sendo por melhor esforço.
Confira o trabalho remanescente no disassembly; o harness não certifica ausência de otimizações.

A coleta guarda CSV bruto, mínimo, máximo, média, mediana, desvio padrão amostral e custo mediano por elemento.
Guarda também `nm`, `size`, disassembly, comandos, hashes, CPU, afinidade, governor e versões.
A frequência registrada é uma observação inicial, não uma frequência fixa durante a campanha.
Se os tempos formarem grupos distintos, examine as condições e a dispersão antes de comparar medianas.
Para entrada vazia, custo por elemento é `null`; o checksum esperado continua zero.
Não há vencedor exigido, razão fixa de tempos ou quantidade fixa de símbolos.
Não há garantia de chamada indireta em cada build.

## Verificar e registrar

O check retorna 0 para contratos aprovados, 1 para violação/starter e 2 para infraestrutura.
O coletor retorna 2 quando a coleta fica incompleta. Consulte `commands.log`; não use resultados parciais como campanha completa.
Os checks conferem vetores independentes, parâmetros e ordem/quantidade das chamadas de `generic` e `dynamic`.
Para `enumerated`, a soma comutativa não revela uma visita em ordem inversa. Revise a ordem no fonte;
o contrato exige a mesma ordem nos três processadores mesmo quando os checksums coincidem.
A revisão do código ainda deve conferir a forma de dispatch, ausência de preparação nos processadores e workload equivalente.

Use o [relato](report-template.md). Registre previsão antes da coleta e anote locais de chamada depois da inspeção.
As medições da preparação validam o instrumento, sem substituir sua investigação.
Estimativa provisória: 7–10 horas. Recalibre-a no piloto coordenado pelo clube.

## Licenças

Código autoral: MIT. Documentação: CC BY 4.0. Dados: CC0 1.0.
Veja [inventário e origem](materials/README.md).
