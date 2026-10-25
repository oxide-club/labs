# Materiais de processos e pipes

Este pacote usa Linux x86-64, C11, Make e Python 3. Disponibilize `printf`, `wc`, `dd`, `true`, `cat` pelo `PATH`. Não é necessário instalar bibliotecas Python.

```sh
make
./build/probe
printf 'status=%s\n' "$?"
./build/probe signal
printf 'status=%s\n' "$?"
make check
```

Os dois comandos `probe` devem produzir status 7 e 143. O starter `oxrun` retorna 2 com diagnóstico; falhas nos checks de execução são esperadas antes da implementação. Complete somente `starter/oxrun.c`.

Contrato: `oxrun run -- programa argumento...` e `oxrun pipe -- programa1 argumento... ::: programa2 argumento...`. Preserve cada argumento de `argv`. Em `pipe`, reserve exatamente um `:::`, com comando dos dois lados. Valide antes de criar filhos. Não interprete uma linguagem de shell.

Use diretamente `fork`, `execvp`, `waitpid`, `pipe`, `dup2` e `close`. Conecte stdout esquerdo a stdin direito e herde stderr. Espere todos os filhos; retome `waitpid` após `EINTR`. Retorne o status do filho em `run` e da direita em `pipe`; use `128+sinal` para sinais, 127 para `execvp/ENOENT`, 126 para outras falhas de execução e 2 com diagnóstico para uso/preparação inválidos. Em preparação parcial, feche file descriptors, encerre os filhos diretos próprios e execute o reaping deles antes de retornar. Pode usar `SIGKILL` nessa recuperação. Os casos obrigatórios não criam descendentes.

O Makefile cria binários em `build/`. Para evitar artefatos no pacote, pode usar `make BUILD=/tmp/oxide-processes-build`. `tests/check.py` aceita `--oxrun CAMINHO --probe CAMINHO`. Cada execução tem timeout de cinco segundos e sessão própria. A limpeza sinaliza somente o grupo dessa execução e espera o processo iniciado pelo runner. Não usa `pkill`, nomes de processos ou PIDs externos. Não execute implementações que alterem sua sessão ou criem descendentes nesta suíte.

Os checks comparam argumentos, stdout, status, diagnóstico, EOF e progresso de 1 MiB. O preflight exige `printf`, `wc`, `dd`, `true` e `cat` pelo `PATH`, além dos binários executáveis `oxrun` e `probe`. Se faltar uma dependência, o runner informa erro de infraestrutura e retorna 3 antes dos checks. Os testes de uso inválido verificam status 2 e diagnóstico; a revisão do código deve confirmar que toda validação precede qualquer `fork`/`exec`. A ausência de um arquivo marcador após a limpeza não provaria ausência de criação ou execução de processos, pois a limpeza poderia matar o filho antes da gravação. Por isso, a suíte não usa um sentinel como evidência dessa obrigação. O runner remove processos ainda ativos no grupo após cada caso; essa limpeza não demonstra que `oxrun` executou o reaping de seus filhos. Status corretos também não demonstram isso.

Revise `waitpid` por PID, os dois caminhos de espera e a retomada após `EINTR`. Quando disponível, registre `strace -f -e trace=process,desc` e relacione cada criação com espera no pai. O trace é evidência da execução observada, não prova geral. Não induza falhas com esgotamento global de processos ou file descriptors. Para falhas raras, uma revisão adicional pode usar wrappers de linking em ambiente controlado: falhar o segundo `fork`, falhar `pipe`/`dup2` e devolver `EINTR` uma vez em `waitpid`. Registre que o wrapper foi realmente acionado e confira fechamento, término e espera dos PIDs criados. O pacote não fornece esse harness nem uma solução central; esses caminhos permanecem uma limitação dos checks públicos.

Preencha `experiments/descriptors.md`. Entregue um relatório com hipótese, ambiente, comandos, resultados observados, explicação, tabela de file descriptors, revisão de falhas e limitações. No repositório, há também `../report-template.md`; o pacote pode ser usado sem esse arquivo.

O fixture sem execução é copiado para arquivo temporário com modo 0600 pelo teste; o teste não depende do modo preservado no download.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** Livre entre implementações POSIX equivalentes; por exemplo C, Rust e Python.

**Linguagens recomendadas:** Rust e Python.

**Restrições técnicas e plataforma:** POSIX; referência Linux x86-64; fork, exec, pipes, descritores e reaping explícitos.

**Tipo de equivalência:** equivalente ao núcleo.

### Contrato independente da linguagem

Preserve argv, status 2/126/127/143, status do lado direito, EOF e pipeline de 1 MiB. Use checks com --oxrun e --probe. Não delegue criação/coordenação do pipeline a shell ou subprocess.run: implemente as operações de processos e descritores estudadas. Registre diferenças do runtime ao fazer fork, especialmente com threads.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código e checks: MIT. Fixtures: CC0-1.0. Documentação: CC BY 4.0.
