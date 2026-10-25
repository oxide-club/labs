# Validação de Alpine com Clang — 25/10/2026

Alpine com Clang executou os checks avaliados de engenharia reversa, segurança de
memória e isolamento. Isso valida a escolha da toolchain para estes materiais;
a integração automática dos ambientes nos Makefiles continua pendente.

## Ambiente observado

- Alpine virt 3.22.7 x86-64, kernel 6.12.114-0-virt.
- ISO SHA256: `c345ec65055908734523e03e81137a2e2f82f0094eb2b6e99bc6e07a7d2a0556`.
- Clang 20.1.8, compiler-rt 20.1.8 e LLVM 20.1.8 para simbolização.
- QEMU com TCG, dois vCPUs e 2 GiB de RAM; KVM não estava disponível.
- Execução como `lab`, UID 1000; interface de rede desativada após instalar pacotes.
- Entrada compartilhada somente para leitura; saída limitada a uma pasta temporária.
- Os 76 pacotes instalados ocuparam 683 MiB no guest. A imagem mínima não representa
  o tamanho da toolchain completa.

A lista completa de versões está em
[evidências do ambiente](evidence/2026-10-25-alpine-clang/environment.txt).
Esta investigação usou os pacotes disponíveis durante a execução. Não demonstra
que a receita automatizada e fixada do ambiente já esteja implementada.

## Resultados

| Verificação | Resultado |
| --- | --- |
| Programa que aloca e libera corretamente | Status 0, stderr vazia |
| Use-after-free com ASan | Diagnóstico com função e linha; status 99 |
| Vazamento com ASan e detect_leaks=1 | LeakSanitizer detectou 64 bytes; status 98 |
| Vazamento com LSan isolado | LeakSanitizer detectou 64 bytes; status 98 |
| Observador original do laboratório 003 | Diagnóstico esperado encontrado; status 0 |
| Checker original 003 contra starter | Rejeitou o código incompleto; status 1 |
| Checker original 003 contra controle corrigido privado | 16 casos; 0 falhas |
| Alvo 002 compilado explicitamente com Clang -O0 | 6 casos públicos passaram |
| Checker 016 contra starter | Rejeitou o TODO com status 125 no filho |
| Checker 016 contra controle privado, fixture Clang -O2 original | Falhou no caso alloc |
| Mesmo checker com fixture -O0 | Passou |
| Mesmo checker com fixture -O2 -fno-builtin-malloc | Passou |
| Mesmo checker após ajuste do Makefile da fixture | Passou |

O primeiro ensaio dos pequenos controles configurava simultaneamente
`ASAN_OPTIONS=exitcode=99` e `LSAN_OPTIONS=exitcode=98`; o runtime retornou 98
inclusive no use-after-free. O diagnóstico estava correto. O ensaio foi repetido
com a opção LSan somente nos controles de vazamento, obtendo os status acima.
Os scripts públicos não foram alterados para acomodar essa diferença.

Os controles corrigidos ficaram fora do repositório, em
`/tmp/oxide-alpine-clang/input/control/`; nenhuma solução foi adicionada ao pacote.
O controle de supervisor foi reutilizado da validação privada anterior.
Os [hashes dos insumos](evidence/2026-10-25-alpine-clang/inputs-sha256.json)
identificam os arquivos usados, mas não substituem os fontes privados.

## Correção da fixture de isolamento

Clang em `-O2` eliminava `malloc` e `free` do binário `probe`, fazendo o cenário
`alloc` retornar 92 sem testar a recusa da allocation pelo limite de memória.
A ausência dos símbolos foi confirmada por `nm -D`; o mesmo fenômeno foi
reproduzido ao compilar no host, sem executar o binário de isolamento.

A receita de `probe` agora acrescenta `-fno-builtin-malloc`. A flag preserva a
chamada real; não altera o supervisor, o limite de 64 MiB, o pedido de 128 MiB,
a expectativa do checker ou as guardas da VM. Um teste de regressão compila com
Clang e inspeciona os símbolos. Ele falhou antes da correção e passou depois.

## Evidências principais

- [Controles dos sanitizers](evidence/2026-10-25-alpine-clang/probe-results.json)
- [Use-after-free simbolizado](evidence/2026-10-25-alpine-clang/uaf-stderr.txt)
- [Vazamento detectado](evidence/2026-10-25-alpine-clang/leak-stderr.txt)
- [16 casos de memória](evidence/2026-10-25-alpine-clang/control-checks.log)
- [6 casos de engenharia reversa](evidence/2026-10-25-alpine-clang/reverse-checks.log)
- [Isolamento após correção da fixture](evidence/2026-10-25-alpine-clang/isolation-fixed-checks.log)

Não houve desativação de sanitizers nem execução dos binários de isolamento no
host. Os resultados não comprovam suporte a outras versões, arquiteturas ou
código adversarial arbitrário.
