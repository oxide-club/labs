# Referências orientadas

Estas fontes ajudam a interpretar o executável; não substituem o contrato local.
Consulta de preparação: 25 de outubro de 2026.

## Ferramentas e método

- [GNU objdump, manual oficial](https://sourceware.org/binutils/docs/binutils/objdump.html).
  Consulte `-d` para gerar instruções e compare com `-S`, que pode intercalar o
  fonte. Pergunta: por que intercalar C mudaria a evidência da primeira etapa?
- [GCC, opções de otimização](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html).
  Consulte os níveis `-O0` e `-O2`. O conjunto exato depende do alvo e da versão.
  Pergunta: quais relações permanecem reconhecíveis após uma transformação?
- [CS:APP, catálogo oficial de labs](https://csapp.cs.cmu.edu/3e/labs.html).
  A descrição do Bomb Lab apresenta a reconstrução pelo executável como método
  de estudo de assembly. A atividade local usa um alvo autoral menor, sem serviço
  de avaliação nem arquivos originais desse desafio.

## Código real: Capstone

[Capstone 5.0.3, `arch/X86/X86Disassembler.c`](https://github.com/capstone-engine/capstone/blob/5.0.3/arch/X86/X86Disassembler.c)
implementa a interface do disassembler x86 e converte dados do decoder em
representações de instruções. Leia a introdução do arquivo, que separa leitura de
prefixos, opcode e operandos da tradução final. Observe como a representação de
uma instrução surge de seus bytes e do contexto de decoding.

**Diferença para o exercício:** Capstone constrói uma representação de instruções;
você interpreta várias instruções e seus saltos para inferir uma decisão.
**Pergunta de leitura:** reconhecer uma comparação basta para saber qual entrada
o programa aceita? Que informação adicional vem do fluxo de controle?

A preparação verificou o conteúdo do
[arquivo bruto na versão 5.0.3](https://raw.githubusercontent.com/capstone-engine/capstone/5.0.3/arch/X86/X86Disassembler.c)
e consultou a ref `refs/tags/5.0.3`, que retornou
`5cca00533dadfe53181f1de3525f859769f69b65`.
O acesso web ao arquivo pelo SHA falhou com `Cache miss`; por isso o link de
leitura usa a versão verificada e registra o SHA da ref para rastreabilidade.
Nenhum código de terceiros foi copiado para o pacote.
