# Guia local dos materiais

Este pacote investiga como instruções de máquina implementam uma decisão.
O alvo `source-archive/gate.c` preserva integralmente o C do Anexo A, antes chamado
`porta.c`. Não há código a completar. Reserve a leitura da função para depois de
reconstruir sua lógica pelo disassembly. O fonte está disponível; guardá-lo é uma
escolha pedagógica e não garante segredo.

## Ambiente e preparação

Use Linux x86-64, GCC, GNU objdump e Python 3. GDB é opcional. Verifique as versões:

```sh
gcc --version
objdump --version
python3 --version
uname -m
```

Execute os próximos comandos na raiz do laboratório, onde estão `index.md` e
`materials/`. Escolha um diretório de trabalho próprio. O script sobrescreve seus
artefatos `gate-O0`, seu disassembly e a cópia guardada do fonte. `--optimized` gera também `gate-O2` e seu disassembly na extensão.

```sh
python3 materials/experiments/prepare.py /tmp/oxide-reverse-lab
python3 materials/checks/check.py /tmp/oxide-reverse-lab/gate-O0
```

O script usa os comandos abaixo em `/tmp/oxide-reverse-lab`, após copiar o C para
`source-archive/gate.c`. O comando não imprime o fonte nem a entrada aceita.

```sh
gcc -std=c11 -Wall -Wextra -Wpedantic -O0 -g -fno-omit-frame-pointer source-archive/gate.c -o gate-O0
objdump -d ./gate-O0 > gate-O0.txt
```

Depois do build, o script move o C para `source-after-analysis/gate.c`, fora do caminho registrado nas informações de depuração.
Leia primeiro `gate-O0.txt`. Não use `objdump -S` nesta etapa: ele pode intercalar
o C. Símbolos e dados de depuração continuam presentes. Para reproduzir os bytes
do build, mantenha iguais toolchain, flags, fonte e caminho de trabalho. Não se
promete igualdade binária entre versões ou diretórios distintos.

## Contrato e checks públicos

`main` recebe exatamente um argumento de entrada. A função de validação exige
seis bytes e aplica condições que você deve inferir. Strings da CLI não incluem
NUL interno. Seis bytes não equivalem necessariamente a seis caracteres Unicode.

| Caso | stdout | stderr | Status |
| --- | --- | --- | ---: |
| Nenhum argumento ou mais de um | vazio | `uso: <argv[0]> CHAVE\n` | 2 |
| `ABC` | `porta fechada\n` | vazio | 1 |
| `AAAAAA` | `porta fechada\n` | vazio | 1 |
| String vazia ou `AAAAAAA` | `porta fechada\n` | vazio | 1 |
| Entrada aceita, deduzida pelo participante | `porta aberta\n` | vazio | 0 |

O `\n` representa um byte de nova linha. A mensagem de uso depende de `argv[0]`;
o check executa o caminho absoluto e verifica esse valor. O check compara status,
stdout e stderr exatos e limita cada execução a cinco segundos. Não contém uma
chave aceita, não procura uma e não imprime argumentos. Sem candidato local,
imprime `6 casos públicos: OK` e informa que o status 0 permanece pendente.

## Investigação obrigatória

1. **Prever:** anote os resultados dos três casos iniciais sem consultar o C.
2. **Observar:** execute os checks e leia `gate-O0.txt`. Localize a chamada da
   verificação a partir de `main`, o teste de comprimento e os acessos aos bytes.
3. **Explicar:** faça uma tabela com trecho de instruções, operandos, operação,
   predicado inferido e destino da decisão. Reconstrua todas as condições, sem
   assumir que toda comparação do programa pertence à validação.
4. **Implementar:** escreva um modelo próprio da decisão e deduza uma entrada
   aceita. Produza também uma entrada quase correta e preveja a comparação que
   a rejeita. Não modifique o alvo nem substitua a análise por busca exaustiva.
5. **Verificar:** execute ambas, registre canais de saída e status e justifique a
   primeira comparação que rejeita a segunda. Só então abra o fonte guardado e
   confronte cada relação inferida. Explique leituras sem sinal, promoções inteiras
   e curto-circuito quando aparecerem na reconstrução.

Guarde sua entrada aceita em um arquivo local com exatamente seis bytes, sem NUL
e sem nova linha final; não o adicione ao pacote. Verifique-a sem imprimir seu conteúdo:

```sh
python3 materials/checks/check.py /tmp/oxide-reverse-lab/gate-O0 --accepted-file /tmp/minha-entrada.bin
```

Esse check adicional exige status 0, `porta aberta\n` em stdout e stderr vazio.
Para a entrada quase correta, execute o alvo no terminal com o argumento escolhido,
anote o status imediatamente com `echo $?` e relacione a rejeição ao disassembly.
Não confunda passar nos checks com concluir a análise: um programa que rejeita
todas as entradas pode passar nos casos públicos.

## Comparar otimizações

Esta extensão é opcional. Após concluir a reconstrução em O0, gere o alvo O2 com `python3 materials/experiments/prepare.py /tmp/oxide-reverse-lab --optimized`. Antes de abri-lo,
preveja se a função permanecerá separada e se a ordem das instruções mudará.
Localize a lógica equivalente em `gate-O2.txt`; se `confere` não aparecer como
símbolo, comece em `main`. Associe pelo menos uma transformação observada às
mesmas restrições, sem esperar igualdade textual ou de endereços.

```sh
python3 materials/checks/check.py /tmp/oxide-reverse-lab/gate-O2
python3 materials/checks/check.py /tmp/oxide-reverse-lab/gate-O2 --accepted-file /tmp/minha-entrada.bin
```

Execute também sua entrada quase correta nos dois alvos. Compare decisão,
status e canais; diferenças estruturais no assembly não implicam mudança de
contrato. Não transforme contagem de instruções estáticas em medição de desempenho.

## Entrega e limites

Entregue o relato, sua tabela e o modelo próprio. Inclua ambiente, comandos,
hipóteses anteriores às observações, entrada aceita, entrada quase correta,
evidência de status 2/1/0 e confronto com o C. Indique quais partes foram inferidas
antes de ler o fonte. Os checks verificam exemplos; a justificativa do fluxo de
controle é necessária e não depende de endereços fixos. Use o modelo de relato
incluído na raiz do pacote. Veja também `../references.md`.

## Linguagens e ambiente

**Linguagem de referência:** C + x86-64.

**Linguagens aceitas:** C no alvo original; Rust somente para comparação.

**Linguagens recomendadas:** Rust para comparação.

**Restrições técnicas e plataforma:** Linux x86-64; preservar gate.c e os alvos O0/O2.

**Tipo de equivalência:** apenas comparativa para outro alvo.

### Contrato independente da linguagem

O executável original é o objeto observado. Outra implementação com as mesmas respostas não substitui seu disassembly. Checks por executável verificam comportamento; a entrega também deve explicar o alvo original.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código original: MIT; documentação: CC BY 4.0; dados de teste originais: CC0 1.0.

Na interface Make, `CC=clang` seleciona Clang. A receita da VM usa essa seleção;
os scripts de preparação mantêm GCC como padrão quando CC não está definido.
