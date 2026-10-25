# Do fonte ao processo

Antes de executar, preveja onde `INPUT_VALUE` desaparece e onde `add_global` permanece indefinido.
Execute `make`, `make check` e `make observe`. Leia os comandos impressos; não atribua todo o trabalho ao driver `cc`.

Preencha pelo menos estas cinco linhas com excertos da sua execução:

| Artefato | Comando produtor | O que contém | Referência/address ainda pendente |
| --- | --- | --- | --- |
| `starter/main.c` | Edição do fonte | A preencher | A preencher |
| `build/main.i` | `cc -E` | A preencher | A preencher |
| `build/main.s` | `cc -S` | A preencher | A preencher |
| `build/main.o` | `cc -c` | A preencher | A preencher |
| `build/program` | `cc main.o operations.o` | A preencher | A preencher |

Compare `symbols.txt`, `object.txt` e `disassembly.txt`. Localize a referência a `add_global` e uma relocation correspondente.
Localize a definição no outro módulo. Explique quais referências dinâmicas podem permanecer no executável.
Leia os dois diagnósticos de linking gerados pelos checks. Identifique a fase da falha e o símbolo envolvido.

Preencha a tabela com uma evidência e uma explicação para cada responsabilidade:

| Componente | Evidência | Decisão ou operação |
| --- | --- | --- |
| Pré-processador | A preencher | A preencher |
| Compilador | A preencher | A preencher |
| Montador | A preencher | A preencher |
| Linker | A preencher | A preencher |
| Kernel | A preencher | A preencher |
| Dynamic loader em espaço de usuário | A preencher | A preencher |

Em `elf.txt`, diferencie section headers de program headers. Localize `LOAD` e `INTERP` quando presente.
Em `maps.txt`, identifique o executável, bibliotecas e stack. Compare offset, permissões e intervalos com os segmentos.
Explique arredondamento por página e possível offset da base; não compare somente números absolutos.
O kernel mapeia segmentos do executável e do interpretador inicial. O dynamic loader resolve dependências e relocations em espaço de usuário.
Justifique essa separação com as leituras, pois maps sozinho não identifica quem solicitou cada mapping.

Em `strace.txt`, localize `execve`, operações relacionadas a bibliotecas/mappings e `write`.
O trace exibe syscalls, não todas as funções C nem os passos internos do kernel durante `execve`.
A chamada `printf` pode usar buffer; explique por que não há correspondência universal de uma função para uma syscall.
Se não houver trace válido, registre a razão e deixe essa parte pendente.

Implemente uma função adicional, preserve a saída e repita os checks em novo diretório.
Anote o que mudou no object file; não entregue apenas arquivos sem comentários interpretativos.
Opcional: repita com PIE explícito e sem PIE. Não desative ASLR no sistema.
