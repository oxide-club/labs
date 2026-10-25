# Materiais para investigar validade e diagnóstico

Execute os comandos a partir da raiz do pacote. O núcleo não depende de completar
os starters históricos. Use Linux, Python 3, GCC ou Clang e runtime ASan/LSan.

## Coleta original

Registre hipóteses para borrowed, owner-null, copy e reset antes de executar:

```sh
python3 materials/experiments/compare.py /tmp/oxide-memory-comparison
```

Escolha um diretório que ainda não existe. Para usar Clang, prefixe o comando com
`CC=clang`. O script compila com C11, O0, símbolos de debug, ASan e frame pointers.
Cada cenário roda em processo próprio, com timeout de dez segundos. Ele guarda:

- `results.json`: plataforma, versão, comando de compilação, opções e status por caso.
- `build.stdout` e `build.stderr`: evidências de compilação.
- `<caso>.stdout` e `<caso>.stderr`: saídas reais de cada processo.

Status zero do runner indica coleta consistente. O caso owner-null precisa ter
status não zero e diagnóstico `heap-use-after-free` com alocação e liberação.
Não fixe o status numérico do sanitizador: runtime e opções de leak podem influenciá-lo.
Os três controles precisam retornar zero com stdout esperado e stderr vazio.
O runner não aceita uma falha genérica de runtime como diagnóstico do UAF.

LeakSanitizer pode falhar sob ptrace ou em um sandbox que bloqueia sua inspeção.
Nesse caso, preserve o erro e repita a coleta em ambiente que suporte o runtime;
não desative a detecção para apresentar a coleta como completa.

## Intervenções do participante

Copie `experiments/lifetimes.c` para um diretório de trabalho. Faça as duas alterações
pedidas no [enunciado](../index.md), em cópias separadas. Não modifique o runner original.

Exemplo de compilação da primeira cópia, a partir da raiz do pacote:

```sh
mkdir -p materials/build
cp materials/experiments/lifetimes.c materials/build/copy-investigation.c
# Edite apenas o cenário copy e registre a previsão antes de executar.
cc -std=c11 -Wall -Wextra -Wpedantic -O0 -g -fsanitize=address -fno-omit-frame-pointer materials/build/copy-investigation.c -o materials/build/copy-investigation
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 materials/build/copy-investigation copy > materials/build/copy.stdout 2> materials/build/copy.stderr
```

Registre também o código de saída imediatamente após a execução (`echo $?`).
Repita com outra cópia para a checagem de geração em reset. Execute apenas o caso
alterado. Ambos devem terminar com status zero e sem diagnósticos; confira os
resultados com sua previsão independente. Não use execução sem sanitizador do
caso owner-null para prever uma saída válida.

## Interpretar reset

A geração pertence ao modelo didático de handle, não ao malloc. Reset incrementa
a geração e escreve outra mensagem na mesma alocação. A view antiga ainda pode
ser lida pelas regras de C nesse cenário, mas já não representa um handle válido.
Essa diferença permite investigar por que ASan não implementa contratos da aplicação.
A checagem que você acrescentar deve impedir o uso lógico inválido, preservando free.

## Inventário e material histórico

- `experiments/lifetimes.c` e `experiments/compare.py`: comparação obrigatória.
- `starter/lifetime.c`, `starter/variation.c`: exercícios históricos opcionais.
- `experiments/observe.py`: coleta histórica de um único UAF.
- `checks/check.py`: valida a correção e CLI históricas; não avalia o novo relato.
- `legacy.md`: contrato, comandos e critérios apenas dessa extensão.

## Linguagens e ambiente

O núcleo observa lifetime de alocações C11 e instrumentação ASan/LSan. Outras
linguagens podem analisar logs e acrescentar comparações; uma rejeição do compilador
Rust não substitui o diagnóstico observado em C.

## Licenças

Documentação original: CC BY 4.0. Código original: MIT. Dados originais: CC0 1.0.
