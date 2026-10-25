# Materiais para investigar representação

Execute a partir da raiz do pacote. Os instrumentos são completos e não dependem de `starter/packet.c`.

## Preparação

Use GCC ou Clang, C11, bytes de oito bits e tipos uint8_t, uint16_t e uint32_t.
Registre `cc --version` e `uname -m`. Crie um diretório de evidências:

```sh
mkdir -p materials/build
cc -std=c11 -Wall -Wextra -Wpedantic -O0 -g materials/experiments/representation.c -o materials/build/representation-O0
materials/build/representation-O0 > materials/build/O0.txt
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/experiments/representation.c -o materials/build/representation-O2
materials/build/representation-O2 > materials/build/O2.txt
```

Registre as hipóteses antes dos comandos. Preserve os arquivos originais; para
cada alteração obrigatória, copie o fonte para `materials/build/` e use nomes
novos nos binários e logs. Guarde o diff do fonte junto ao relato.

## Ler a observação

`word` é um valor numérico. `host` é sua representação local. `LE` e `BE` são
codificações externas explícitas. `wrong` lê a sequência LE como se fosse BE.
Ela pode coincidir com a word quando a entrada não distingue as ordens.

As linhas A/B mostram tamanho total, alignment e offsets. Some as larguras dos
campos (1, 4 e 2 bytes) e compare com os intervalos e tamanho total observados.
Não leia padding nem presuma seu conteúdo. A linha final compara os três campos
e os sete bytes serializados; `memcmp` é usado somente nesses arrays externos.

O código já fornece as operações necessárias à primeira coleta. As intervenções
obrigatórias estão no [enunciado](../index.md): quarta word, campo marker e
round-trip que esconde desacordo sobre o formato. Elas exigem uma previsão e logs próprios.

## Verificar suas alterações

Compile também suas cópias com UBSan e execute os mesmos casos:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O1 -g -fsanitize=undefined -fno-sanitize-recover=all materials/experiments/representation.c -o materials/build/representation-ubsan
materials/build/representation-ubsan
```

Substitua o caminho do fonte pela cópia alterada para verificar sua instrumentação.
Status zero sem `runtime error` é uma verificação auxiliar, não avaliação da explicação.

## Inventário

- `experiments/representation.c`: instrumento completo do núcleo.
- `legacy.md`: contrato e comandos da extensão histórica opcional.
- `starter/packet.h`, `starter/packet.c`: API e starter incompleto dessa extensão.
- `checks/tests.c`, `fixtures/vectors.csv`: verificações e dados do header histórico.
- `experiments/observe.c`: observação histórica que depende de completar `packet.c`.

## Linguagens e ambiente

O núcleo observa objetos C11 e exige executar o instrumento C. Outras linguagens
podem analisar saídas ou acrescentar comparações. A extensão histórica admite
adaptação de linguagem conforme seu contrato. Não substitua layout C por uma
simulação e apresente o resultado como observação da ABI.

## Licenças

Código original: MIT. Fixtures: CC0-1.0. Documentação: CC BY 4.0.
