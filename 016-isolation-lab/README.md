# Isolamento de Processos

Leia o [enunciado](index.md), o [guia de materiais](materials/README.md) e o
[contrato](materials/contract.md). O supervisor é um starter com TODO: compilar não
significa satisfazer os checks. Código MIT, documentação CC BY 4.0 e dados de teste
originais CC0 1.0; os avisos gerais acompanham o pacote.

É permitido compilar no host. Execute os programas e os checks dinâmicos apenas
em **VM descartável**. O [percurso teórico](experiments/theory.md) permite estudar os
mecanismos sem VM e registra a verificação prática como pendente.

Em 25/10/2026, os checks foram executados em VM Alpine descartável no QEMU, como
usuário sem privilégios. Uma implementação privada passou; cinco mutantes foram
rejeitados. O starter continua incompleto. A solução didática não é adequada para
execução de código adversarial em produção.

Use o [modelo de relato](report-template.md), gerado do template central do repositório.
As [referências](references.md) incluem leitura orientada de código real em revisão fixa.

## Observação inicial de processos próprios no host

Antes da etapa guardada, observe somente ferramentas prontas e benignas: execute
`sleep 1 &`, anote `$!` e use `wait "$!"` no mesmo shell para recolher esse filho.
Explique a diferença entre iniciar, esperar e obter o status. Isso atende à primeira
etapa de processos próprios; não executa o supervisor nem as fixtures deste pacote.
A compilação continua permitida no host. `probe`, supervisor, checks e experimentos
de isolamento mantêm todas as guardas e só executam na VM descartável.

A VM dos checks exige `PR_SET_CHILD_SUBREAPER` e procfs com
`CONFIG_PROC_CHILDREN` (`/proc/<pid>/task/<pid>/children`). As janelas de tempo foram verificadas nessa VM; isso não garante latência em
qualquer ambiente. Registre a carga e as condições de cada execução.
