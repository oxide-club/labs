# Validação dos demais Makefiles — 25/10/2026

Os 15 laboratórios fora da integração QEMU foram exportados pela função real
`labFiles` do website para `/tmp/oxide remaining packages`, sem arquivos do
repositório pai. Foram executados 133 comandos: help, setup, build, test,
verify-preparation, run e clean em 19 combinações de referência/variante.
O laboratório 017 usou MODE=cpu nessa matriz.

Todos os comandos help, setup, build, verify-preparation e clean dessa matriz
retornaram zero. Falhas de starters em test/run foram mantidas; nenhum starter
foi implementado para fazer os checks passarem.

| Lab | Variante | test | run |
| --- | --- | --- | --- |
| 001 | reference | 2 | 0 |
| 004 | reference | 2 | 0 |
| 005 | reference | 2 | 2 |
| 005 | rust | 2 | 2 |
| 006 | reference | 2 | 2 |
| 007 | reference | 0 | 2 |
| 008 | reference | 2 | 2 |
| 009 | reference | 2 | 2 |
| 009 | rust | 2 | 2 |
| 010 | reference | 2 | 0 |
| 010 | rust | 2 | 0 |
| 011 | reference | 2 | 2 |
| 011 | go | 2 | 0 |
| 012 | reference | 2 | 0 |
| 013 | reference | 2 | 2 |
| 014 | reference | 2 | 2 |
| 015 | reference | 2 | 2 |
| 017 | reference / cpu | 0 | 0 |
| 018 | reference | 2 | 0 |

Os números são os status do GNU Make no host (0: sucesso; 2: erro). Em 007 e
013, run retornou 2 no sandbox por bloqueio de ptrace; repetido com permissão
para strace, ambos retornaram 0. As evidências parciais do erro foram preservadas.
Os demais erros correspondem aos starters incompletos.

Adicionalmente, `make run EXPERIMENT=model` no 010 passou;
`make run EXPERIMENT=measure` no 018 recusou a medição após falhar nos checks,
como previsto para o starter original.

## Recursos GPU

A investigação encontrou nvcc instalado, mas nenhum dispositivo CUDA acessível.
Antes da correção, setup retornava zero apenas por encontrar as ferramentas.
Agora setup compila e executa a sonda já existente probe.cu: retornou erro com
`no CUDA-capable device is detected`, sem executar kernels do participante.
`make build MODE=gpu` compilou os binários CUDA com sucesso mesmo sem dispositivo,
confirmando a separação entre build e execução. Os testes de regressão cobrem
recursos disponíveis e indisponíveis com uma
sonda substituta, sem exigir GPU na suíte local. Compilação e validação de
kernels CUDA são coberturas diferentes; não houve validação de kernels GPU.

## Evidências

[Matriz de comandos e status](evidence/2026-10-25-make-remaining/results.json).
Logs adicionais em [evidências desta validação](evidence/2026-10-25-make-remaining/).
A validação QEMU dos outros três laboratórios está em
[Alpine com Clang](alpine-clang-validation.md).

Verificação final: 46 testes Python passaram; gerador Make, templates de relatórios
e modelo de cache sem divergências; 18 laboratórios sem erros estruturais.
Revisão independente da continuação concluída sem achados materiais.
