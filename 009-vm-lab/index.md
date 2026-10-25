---
title: Laboratório de Máquinas Virtuais
area: compilation-execution
slug: 009-vm-lab
summary: Implemente uma VM de stack com saltos, variáveis e falhas observáveis.
question: Como instruções alteram o estado de uma máquina abstrata?
draft: false
publishedAt: 2026-10-25
topics: [Máquinas virtuais, Interpretadores]
prerequisites: [Funções, Arrays, Stacks, Inteiros]
tools: [Python 3]
environment: Python 3.10 ou superior e biblioteca padrão em Linux
difficulty: intermediate
---

## O que vamos investigar

Uma máquina virtual (VM) executa instruções sobre um estado definido pelo interpretador.
O contador de programa (PC) identifica a próxima instrução. O dispatch seleciona a ação de cada opcode.
Investigue como uma alteração do PC produz um laço e como limites tornam essa execução controlável.
Você deve implementar o dispatch, a validação e as transições na linguagem escolhida, sem `eval`, `exec` ou bibliotecas de VM.

### Contrato técnico

Na versão Python, a API obrigatória é `run(source: str, budget: int = 1000) -> dict` em `materials/vm.py`.
Cada chamada cria estado independente: PC 0, stack vazia, oito variáveis iguais a zero, steps 0 e trace vazio.
O chamador fornece `str` e budget inteiro de 1 a 10000, sem bool; outros budgets geram `ValueError`.

O formato é textual, não bytecode binário. Cada linha não vazia contém um opcode maiúsculo e seus operandos, separados por espaço ASCII ou tab.
Permita espaços ASCII e tabs antes e depois de cada instrução. Linhas com apenas esses caracteres são vazias e são ignoradas. Aceite LF e CRLF; rejeite CR isolado. Não aceite comentários, labels ou outros separadores.
Um inteiro usa a gramática `-?[0-9]+` ASCII: zeros à esquerda e `-0` são permitidos; `+1`, hexadecimal e números Unicode são rejeitados.
São permitidos de 1 a 256 instruções e no máximo 16384 caracteres, incluindo quebras de linha.
O PC é o índice da instrução após remover linhas vazias, começando em zero; não é o número da linha.
A VM deve validar o programa inteiro antes de executar, inclusive instruções inalcançáveis.

Todos os valores são inteiros com sinal de 32 bits, de -2147483648 a 2147483647.
Overflow gera erro; não há wraparound. A stack comporta no máximo 32 valores, com topo à direita.
As variáveis têm índices de 0 a 7 e começam inicializadas. Não há divisão nesta ISA.

| Instrução | Operando | Efeito em uma execução bem-sucedida |
| --- | --- | --- |
| PUSH n | inteiro de 32 bits | Adiciona n ao topo. |
| POP | nenhum | Remove o topo. |
| ADD | nenhum | Substitui os dois topos a, b por a+b. |
| SUB | nenhum | Substitui os dois topos a, b por a-b; b era o topo. |
| LOAD i | índice 0..7 | Adiciona o valor da variável i ao topo. |
| STORE i | índice 0..7 | Remove o topo e grava na variável i. |
| JMP p | índice 0..N-1 | Define PC=p. |
| JZ p | índice 0..N-1 | Remove o topo; se era zero, define PC=p; senão, PC+=1. |
| HALT | nenhum | Encerra com sucesso; mantém o PC nesta instrução. |

As demais operações avançam PC em um. Cada instrução concluída, inclusive HALT, incrementa steps.
HALT pode deixar valores na stack. A presença textual de HALT não é obrigatória.
Se PC=N, retorne `pc_out_of_range`. Se steps=budget antes da próxima busca, retorne `step_limit`.
Verifique o PC antes do budget, para fixar a precedência quando ambos falham.
Um laço sem HALT termina pelo budget. Não busque uma instrução extra nesse caso.

O resultado contém exatamente `status`, `error`, `pc`, `stack`, `variables`, `steps`, `trace`.
`status` é `halted` ou `error`; `error` é null em sucesso ou um código abaixo.
Cada item do trace contém exatamente `pc`, `opcode`, `stack`, com cópia da stack **antes** da tentativa da instrução.
Inclua a tentativa que falha por stack ou overflow. Não inclua buscas fora do programa nem tentativas após esgotar budget.
O trace não inclui operandos nem variáveis. O estado final deve permitir comparar ambos separadamente.

| Código | Condição |
| --- | --- |
| invalid_program | Fonte excede limite, está vazia, opcode/gramática/aridade inválidos, literal fora da faixa, variável ou salto inválido. |
| stack_underflow | POP, STORE ou JZ sem topo; ADD ou SUB com menos de dois valores. |
| stack_overflow | PUSH ou LOAD com 32 valores. |
| integer_overflow | Resultado de ADD ou SUB fora da faixa. |
| pc_out_of_range | Execução alcança PC=N sem HALT. |
| step_limit | Não há budget para executar a próxima instrução. |

Uma falha de validação retorna o estado inicial e `invalid_program`, sem trace.
Uma falha de execução preserva PC, stack e variáveis anteriores à instrução; não incrementa steps.
O resultado é terminal. Nenhuma instrução posterior deve executar. Uma nova chamada começa do zero.
Exceções inesperadas do interpretador são defeitos de implementação, não erros do programa interpretado.

## Antes de começar

### Linguagens e ambiente

Referência: **Python**. Aceitas: Livre; por exemplo C, Rust, Go e Python.
Recomendadas: Rust, Go e Python. ISA textual publicada; int32 com sinal; validação integral e dispatch próprio.
Materiais oficiais: Python existente; Rust: `materials/starter/rust/`.
Equivalência: equivalente sob contrato adaptado.
Consulte [as diferenças e o contrato de participação](materials/README.md#linguagens-e-ambiente).
Os starters são opções de preparação; sua linguagem não é obrigatória.

Conheça funções, listas, condicionais, loops e stacks. Use Python 3.10 ou superior, sem dependências externas.
Leia [o guia local](README.md). Todos os comandos partem deste diretório.

## Materiais

[O guia de materiais](materials/README.md) descreve o starter e os programas textuais.
[Os checks](checks/check.py) comparam estados e traces contra [fixtures independentes](materials/cases.json).
[O experimento](experiments/trace.md) orienta a investigação do fluxo de controle.

## Etapas da investigação

1. **Prever:** desenhe à mão o PC e a stack de expression.txt e branch.txt antes de consultar os fixtures. Registre a ordem de SUB e o consumo de JZ.
2. **Observar:** leia os traces de referência. Marque a instrução pulada e compare cada linha com sua previsão.
3. **Explicar:** relacione o PC ao próximo opcode. Explique por que laço não exige uma instrução própria e por que overflow não pode remover operandos.
4. **Implementar:** complete `materials/vm.py`. Mantenha validação separada das transições para rejeitar também código inalcançável inválido.
5. **Verificar:** execute `python3 checks/check.py`. Investigue a primeira divergência e depois execute o experimento de trace.

## Critérios de conclusão

Os checks devem terminar com status zero. Entregue a implementação, três programas válidos e três inválidos, e um trace explicado.
Justifique limites, atomicidade de falhas, budget e diferença entre falha interpretada e defeito do interpretador.
Registre uma previsão que mudou após observar a execução. Os checks públicos cobrem exemplos, não demonstram correção para toda entrada.

## Extensões opcionais

Você pode criar um assembler que converta labels para índices ou definir bytecode binário.
Preserve a ISA obrigatória e documente decodificação, truncamento e compatibilidade antes de alterar o formato.
Frames e funções também são opcionais e exigem novos contratos.

## Participação no clube

Compartilhe uma tentativa com o menor programa que reproduz sua dúvida, o estado previsto e o estado observado.
Use [o modelo de relato](report-template.md). Ao revisar outra tentativa, explique qual transição sustenta sua conclusão.

## Referências e atividades relacionadas

Leia [as referências orientadas](references.md). Relacione o PC da VM ao disassembly estudado em engenharia reversa.
