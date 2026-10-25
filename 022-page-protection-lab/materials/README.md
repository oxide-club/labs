# Materiais — Page protection e access violations

Pacote preparado para revisão, revisão `022-preparacao-v2`. O supervisor continua sendo trabalho do participante. Não há solução completa distribuída.

## Linguagens e ambiente

Núcleo C11 e assembly x86-64, Linux, ABI System V. Python 3 e strace verificam o supervisor. Consulte a [VM de referência](vm.md).

## Inventário

| Arquivo | Uso |
| --- | --- |
| `starter/c/pageprobe.c` | Supervisor incompleto, compila e retorna 2 |
| `starter/c/probe.S` | Sonda original de leitura/escrita de um byte |
| `starter/c/probe.h` | Interface da sonda, ABI System V x86-64 |
| `starter/c/Makefile` | Build C11 e inspeção com objdump |
| [audit.md](audit.md) | Escopo da auditoria e disassembly observado |
| [records.md](records.md) | IDs, JSONL, timeout e agregação de resultados |
| [matrix.md](matrix.md) | Matriz vazia de hipóteses e observações |
| [LICENSE-MIT.md](LICENSE-MIT.md) | Licença dos fontes e checks originais |
| [checks/check.py](../checks/check.py) | Checks de comportamento e auditoria de terminação real |
| [checks/audit_trace.py](../checks/audit_trace.py) | Coleta strace própria e confronto com JSONL |
| [checks/test_audit.py](../checks/test_audit.py) | Oito regressões do parser com dados sintéticos, sem medições simuladas |
| [vm.md](vm.md) | Distribuição, recursos, preparação e reprodução da VM |
| [vm-assets.json](vm-assets.json) | URLs e SHA-256 da ISO e dos pacotes fixados |

## Responsabilidade do participante

Implemente `pageprobe`, isole cada sonda num filho e construa a investigação definida no [enunciado](../index.md). Explique previsões, observações, mecanismos e limites. A sonda do clube não substitui o supervisor. Use os comandos do [guia local](../README.md).

## Validação e limites

Build e comandos executados em cópia isolada em `/tmp`. Starter rejeitado; referência privada aprovada; oito mutantes rejeitados por requisitos distintos. As soluções e o guia reservado ficam fora do pacote. Os registros de preparação pertencem às evidências do repositório, não às previsões do participante.

O guia local descreve os ambientes observados e a VM. A revisão independente identificou um falso positivo de saída 139; esta revisão o rejeita pela terminação real. Piloto e revisão humana de publicação continuam pendentes. Preserve `draft: true`.

## Origem e licenças

Especificação: atividade 33 do caderno curricular de 25/10/2026. Redação: Português Técnico Claro 1.1. Fontes C, assembly, Makefile e checks Python são originais Oxide Club, 2026, MIT. Documentação e matriz vazia: CC BY 4.0. Não há código copiado das referências externas.
