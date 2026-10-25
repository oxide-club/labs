# Guia dos materiais

Use Linux x86-64, GCC ou Clang com C11, GNU Make, GNU binutils (`nm`, `readelf`, `objdump`), Python 3 e `strace` com a opção `--kill-on-exit`.
Execute os comandos neste diretório. O Makefile imprime cada comando real e mantém os estágios intermediários.

```sh
make
make check
make observe
```

Para Clang, use `make CC=clang BUILD=build-clang` e acrescente essas mesmas opções aos outros alvos.
Use um diretório novo quando mudar compilador ou flags: Make não detecta mudanças de flags.
Os caminhos de build devem ser simples, sem espaços, por causa da sintaxe do Makefile.

| Arquivo | Função |
| --- | --- |
| `starter/main.c` | Literal, macro, chamada externa, libc e espera controlada |
| `starter/operations.c` | Global definida e função externa |
| `starter/operations.h` | Declarações compartilhadas |
| `Makefile` | Pré-processamento, tradução, montagem e linking separados |
| `tests/check.py` | Saída/status determinísticos e dois erros de linking |
| `experiments/observe.py` | Inspeção ELF, maps e tentativa de strace |
| `experiments/investigation.md` | Perguntas e tabelas para o relato |

`build/` é gerado localmente. Os scripts sobrescrevem apenas seus arquivos de evidência.
Não distribua binários como fontes. Os diagnósticos ficam em `undefined.stderr.txt` e `duplicate.stderr.txt`.
O script de observação mantém stdin aberto, espera prontidão por até cinco segundos e captura maps.
Depois fecha stdin, espera o término e executa reaping do processo. Em falhas, encerra somente seu processo próprio.
A execução sob `strace` tem limite de dez segundos e usa o programa sem espera; não cria descendentes próprios. `--kill-on-exit` encerra o processo observado se o tracer for encerrado no timeout.
Se `/proc` estiver restrito, a coleta falha com diagnóstico. Se faltar `strace`, registra pendência e preserva a coleta parcial.

Os checks cobrem saída normal, byte/EOF, uso inválido, ELF e símbolos. Não exigem mensagens exatas do linker.
Não medem desempenho e não avaliam sua explicação. Faça a alteração pedida no enunciado, preserve o contrato e reconstrua em outro diretório.

Use o modelo central `templates/report-template.md` no repositório, ou o `report-template.md` incluído no pacote.
Registre ambiente, previsões, comandos, resultados, cinco artefatos, tabela de responsabilidades, alteração e limitações.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** C no núcleo C/ELF; Rust e C++ em comparações.

**Linguagens recomendadas:** Rust e C++.

**Restrições técnicas e plataforma:** Linux/ELF e etapas de compilação C observáveis.

**Tipo de equivalência:** apenas comparativa para outras linguagens.

### Contrato independente da linguagem

Preserve pré-processamento, compilação, montagem, linking, símbolos e erros controlados. Artefatos Rust ou C++ permitem comparação, mas não substituem as etapas C. Não imponha instruções ou endereços idênticos entre compiladores.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

`make observe` exige strace ≥ 6.6 para `--kill-on-exit`. O arquivo `strace.txt` é filtrado a `execve`, `openat`, `mmap`, `mprotect`, `read`, `write` e `exit_group`; não é o histórico completo de syscalls. O filtro destaca carregamento, memória e I/O.

## Licenças

Código original MIT; documentação CC BY 4.0. Consulte os avisos de licença incluídos na distribuição.
