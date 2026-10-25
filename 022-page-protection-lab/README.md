# Guia local — Page protection e access violations

Leia o [enunciado](index.md). **Em elaboração.** O pacote executável está preparado para revisão; `draft: true` permanece até revisão e piloto.

## Ambiente

Linux x86-64, ABI System V, C11, `make`, `cc`, `objdump`, Python 3, `strace` e `/proc/self/maps`. Execute como usuário comum em processos próprios. A validação local usou Omarchy 4.0.6, kernel 7.2.8-9-omarchy, GCC 16.2.1, Binutils 2.47 e Python 3.14.8. A [VM de referência](materials/vm.md) fixa imagem, pacotes, recursos e preparação. Não requer rede, bibliotecas externas, privilégios de root ou mudanças globais.

Estimativa curricular: 8–12 horas, incluindo análise. Recalibre-a no piloto coordenado pelo clube.

## Preparar e executar

A partir deste diretório, copie o pacote para uma pasta de trabalho:

```sh
cp -R . /tmp/page-protection-participant
cd /tmp/page-protection-participant
make -C materials/starter/c
make -C materials/starter/c audit
./materials/starter/c/pageprobe --case all --timeout-ms 200
```

Use uma pasta de destino nova. O build deve terminar com 0. O starter termina com 2 e informa que falta implementar o supervisor. Isso é uma falha intencional de implementação, não resultado experimental. Edite `materials/starter/c/pageprobe.c`, usando a [sonda auditada](materials/audit.md). Preencha a [matriz](materials/matrix.md) antes de executar.

Implemente a supervisão, as transições e o [formato dos registros](materials/records.md). Preserve a sonda fornecida. Desative core dumps apenas no processo experimental, se necessário; não modifique a configuração global de coredump.

## Verificar

```sh
python3 checks/check.py ./materials/starter/c/pageprobe --audit-out /tmp/pageprobe-audit
```

O starter deve ser rejeitado com status 1 (`matriz incompleta`). Uma implementação correta deve retornar 0 nos checks. Status 2 dos checks significa ambiente incompatível ou strace/ptrace indisponível, sem aprovação. Os checks têm um prazo externo de 20 segundos por comando e encerram o grupo de teste se necessário.

Após implementar, preserve registros e traces:

```sh
./materials/starter/c/pageprobe --case all --timeout-ms 200 > matrix.jsonl
strace -f -e trace=mmap,mprotect,munmap,clone,wait4,kill,close -o syscalls.log ./materials/starter/c/pageprobe --case all --timeout-ms 200
```

O check executa uma coleta independente com strace e exige que cada filho termine conforme o registro. Também confere o status real de wait4. Se o runner bloquear ptrace, registre a indisponibilidade e repita em ambiente permitido, sem alterar políticas globais. Use um diretório `--audit-out` novo para cada execução. O loader mapeia código executável normalmente; a restrição de execução é da região experimental. Identifique seus intervalos no trace.

Para auditar novamente os arquivos de uma coleta própria:

```sh
python3 checks/audit_trace.py --trace /tmp/pageprobe-audit/all.strace --records /tmp/pageprobe-audit/all.stdout
```

Esse modo não atesta a origem dos arquivos. A aprovação completa usa a coleta criada pelo check, que distingue `killed by SIGSEGV` de `exited with 139`.

Teste o parser da auditoria separadamente:

```sh
python3 checks/test_audit.py
```

Os oito testes usam dados sintéticos identificados; não aprovam o supervisor nem substituem a coleta real.

## Registrar

Use o [modelo de relato](report-template.md), sem editar sua cópia canônica. Entregue matriz, comandos, registros JSONL, mapeamentos das transições, disassembly, traces e inventário de recursos encerrados. Os checks não substituem explicações causais nem revisão do mecanismo.

## Licenças

Documentação original: CC BY 4.0. Código original: MIT, conforme [aviso](materials/LICENSE-MIT.md). A matriz vazia é documentação original. Não há fixtures ou código de terceiros distribuídos. Revisão do pacote: `022-preparacao-v2`, 25/10/2026.
