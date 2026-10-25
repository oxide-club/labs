# Guia local — Atomics e memory ordering

Leia o [enunciado](index.md). O laboratório está aprovado para publicação, com `draft: false`.
A validação do instrumento não substitui sua investigação.

## Ambiente

Validado em Linux x86-64, Rust/Cargo 1.98.1, LLVM 22.1.8 e Python 3.14.8.
Loom está fixado em `=0.7.2`; dependências transitivas estão no lock distribuído.
Use Rust 1.98.1 no PATH. O runner chama `cargo` e `rustc` desse PATH.
Se o shim rustup falhar, use o diretório `bin` da toolchain já instalada.
Não é necessário atualizar Rust para executar os comandos.

A exploração usa dois papéis, `max_threads=2`, `max_branches=1000` e nenhuma restrição de preempções.
Não há corte por duração ou número de permutações no Builder.
O runner remove variáveis `LOOM_*` e impõe prazo externo de 180 segundos por comando.
Uma interrupção por prazo ou limite não aprova o modelo.

## Preparar e executar

Execute a partir deste diretório, com o pacote extraído:

```bash
python3 checks/test_support.py
python3 checks/check.py --build-only
python3 checks/check.py --std-only --build-only
python3 checks/check.py --std-only
python3 checks/check.py
```

Os dois builds e o teste do classificador devem retornar 0.
Os dois últimos comandos retornam 1 no starter, com `not yet implemented`.
Implemente `publish` e `try_read` em `materials/starter/src/lib.rs`.
Preserve os tipos instrumentados e as ordenações de cada variante do contrato.
Repita os dois últimos comandos após implementar.
O runner cria uma cópia temporária e restaura `Cargo.lock` de `Cargo.lock.txt`.
Ele instala os testes públicos nessa cópia. Não altera seu código.
A primeira compilação precisa das dependências do lock, baixadas pelo Cargo ou disponíveis em cache.

Para guardar a saída completa após implementar:

```bash
python3 checks/check.py > model.log 2>&1
python3 checks/check.py --std-only > local.log 2>&1
```

O resultado local contém 1.000 tentativas por variante: `None`, `Some42` e `Some0`.
Não existe frequência esperada para esses resultados locais.

## Verificar e interpretar

Código 0 significa que os checks solicitados passaram; não significa conclusão do laboratório.
Código 1 indica starter incompleto, propriedade divergente ou evidência insuficiente.
Leia o diagnóstico completo para distinguir essas situações.
Código 2 indica indisponibilidade, timeout externo, erro de build ou limite de exploração excedido.
Os diagnósticos identificam esses estados separadamente.

O caso fraco exige simultaneamente um teste falho e o diagnóstico específico
`PUBLICATION_VIOLATION ready=true data=0 observed=Some(0)`.
`MODEL_OBSERVATION` registra o retorno capturado antes de `join`, com variante e número da execução.
Um panic genérico, um limite excedido ou zero testes executados não atende ao check.
`RETURN_DIAGNOSTIC` é uma dedução do retorno, não um trace das operações atômicas.
Confira a correspondência com os loads na implementação e construa a explicação exigida pelo roteiro.
`MODEL_SUMMARY` informa totais `None`, `Some42`, `Some0`, `Other` e a condição de término.
`complete` indica que o Builder retornou; `interrupted` indica panic e contagens parciais.
A variante fraca interrompe a busca no primeiro contraexemplo. Não interprete seus totais como exploração completa.

As variantes corretas precisam terminar sem violação e alcançar tanto `None` quanto `Some(42)`.
O check rejeita a ausência de publicação observada, em vez de aprovar uma propriedade sem evidência relevante.
Não há exigência de uma quantidade fixa de execuções exploradas.
O runner confere a correspondência entre registros individuais e totais; resumo isolado não basta.
`MODEL_CONFIG` registra os limites; cada invocação de teste identifica a campanha no log do runner.

Os contadores externos usam atomics `std` e não são parte do estado compartilhado modelado.
Somente o consumidor os acessa, depois de `join`, usando o retorno capturado anteriormente.
O produtor não recebe os contadores e não comunica dados por eles.
A coleta não altera os loads, stores nem a ordem relevante do experimento.

O harness mantém o consumidor no corpo do teste e o produtor numa thread criada.
O consumidor registra o retorno antes de `join`. Não acrescente sleeps ou sincronização auxiliar.
Os checks de comportamento não certificam a estrutura do código: revise também acessos e ordenações.

## Registrar

Use o [relato](report-template.md). Registre previsões antes da execução.
Separe observação local, exploração do modelo e argumento de happens-before.
Explique reads-from, limites de Loom e por que `None` não viola o contrato.
Confira manualmente as ordenações de cada operação; os checks não distinguem toda substituição por ordem mais forte.
No teste local, a latência de criar a thread pode favorecer `None`; não use sua frequência como garantia.
Loom 0.7.2 não emula reordenações dentro de uma thread. O contraexemplo aqui explora a leitura de valor antigo.
Esse limite não exclui outros comportamentos permitidos pelo modelo de memória.
Estimativa provisória: 8–12 horas. Recalibre-a no piloto coordenado pelo clube.

## Licenças

Código autoral Oxide Club: MIT. Documentação: CC BY 4.0. Dados: CC0 1.0.
Veja [origem e inventário](materials/README.md). Loom e dependências conservam suas licenças próprias.
