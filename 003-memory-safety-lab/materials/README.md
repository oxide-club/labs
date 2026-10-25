# Guia dos materiais — Segurança de Memória

Este guia funciona no pacote baixado. Os comandos partem de `materials/`.
Use `cd materials` a partir da raiz do laboratório. É necessário Python 3 e
GCC ou Clang com runtimes ASan/LSan em Linux x86-64. Não há instalação de módulos Python.

## Observar antes de corrigir

`starter/lifetime.c` é o original `vida.c` com nome autorizado em inglês.
Não há correção pronta nos materiais. Antes de editar, execute:

```sh
python3 experiments/observe.py /tmp/oxide-memory-first-observation
cat /tmp/oxide-memory-first-observation/status.txt
cat /tmp/oxide-memory-first-observation/asan.txt
```

O diretório de saída deve ser novo. O script não o apaga nem sobrescreve.
Ele usa `-std=c11 -Wall -Wextra -Wpedantic -O0 -g -fsanitize=address
-fno-omit-frame-pointer`, aguarda no máximo dez segundos e registra o processo.
Espera-se `heap-use-after-free`, `freed by` e `previously allocated` no diagnóstico.
Um diagnóstico diferente requer investigação; ele não confirma o fenômeno esperado.
Para executar diretamente:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O0 -g -fsanitize=address -fno-omit-frame-pointer starter/lifetime.c -o /tmp/oxide-lifetime
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 /tmp/oxide-lifetime
```

Identifique função e linha do acesso, da liberação e da allocation. Desenhe a visão
obtida por borrowing e o proprietário. Explique por que `m.texto = NULL` não atualiza a cópia
armazenada em `visao`. Guarde a observação original antes de alterar o arquivo.
Após a correção, o script de observação deixa de aceitar o programa: ele verifica
o defeito original. Para verificar a correção, use os checks abaixo.

## Corrigir e variar

Corrija `starter/lifetime.c`: mantenha a allocation dinâmica da string `Oxide Club`,
a saída `Club\n`, status 0 e uma única liberação após todos os acessos. Se a
allocation falhar, retorne 2. Não libere a visão obtida por borrowing separadamente.

Implemente `starter/variation.c` como `variation DESLOCAMENTO`. Esta sintaxe é
uma decisão nova do laboratório; o anexo original fixa valores e resultados,
mas não uma CLI. Aceite exatamente um argumento não vazio de dígitos ASCII,
sem sinais ou espaços, com valor entre 0 e 10. Zeros à esquerda são válidos.
Rejeite valores excessivos sem overflow na conversão e antes de formar a visão.
O bloco tem 11 bytes; o índice 10 contém o terminador zero. O offset 11
não inicia uma string válida e deve ser rejeitado antes de formar esse ponteiro.

| Argumento | stdout exata | Status |
| --- | --- | ---: |
| `0` | `Oxide Club\n` | 0 |
| `6` | `Club\n` | 0 |
| `10` | `\n` | 0 |
| `11` ou entrada inválida | vazia | 2 |

Em erro de argumento, stderr é exatamente
`Erro: use um deslocamento decimal entre 0 e 10.\n`. Em sucesso, stderr é vazia.
Em falha de allocation, retorne 2 e deixe stdout vazia; stderr não tem texto fixado.
Preserve allocation dinâmica, cópia dos 11 bytes e liberação única na variação.
Explique o caminho de falta de memória por revisão; os checks não o injetam.

## Verificar a implementação

```sh
python3 checks/check.py
```

Espere inicialmente falhas. Após concluir, espere `16 casos; 0 falhas`, status 0.
Os checks compilam ambos os fontes em diretório temporário e comparam bytes e
status. Eles ativam detecção de memory leaks e não aceitam stderr em sucesso.
Incluem 0, 6, 10, 11, negativos, sinais, espaços, sufixos, vazio, valor decimal
muito grande e quantidade incorreta de argumentos. Cada execução tem timeout.
Use `--source-dir CAMINHO` para testar outra cópia dos dois fontes.
Use `CC=clang` para selecionar Clang. Os checks incluem também `0006`; acrescente casos próprios. Os checks são amostras: revisar a ordem da validação e o lifetime é
obrigatório, pois ASan não prova que nenhum ponteiro inválido foi apenas formado.

Se LeakSanitizer reportar que não funciona sob ptrace ou restrições do ambiente,
registre a falha de infraestrutura e repita fora dessa restrição. Desativar LSan
serve apenas ao diagnóstico; não cumpre a verificação de memory leaks do núcleo.
Registre compilador, flags, arquitetura e limites da evidência. Use o
[modelo de relato](../report-template.md).

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** C no núcleo; C++ e Rust para comparação.

**Linguagens recomendadas:** C++ e Rust.

**Restrições técnicas e plataforma:** AddressSanitizer no núcleo C; observar allocation, deallocation e acesso inválido.

**Tipo de equivalência:** apenas comparativa para outras linguagens.

### Contrato independente da linguagem

Preserve lifetime.c e a saída Club, os offsets 0/6/10/11 e os critérios de diagnóstico/correção. Um programa Rust seguro pode impedir a construção de uma referência inválida; essa rejeição não equivale ao diagnóstico dinâmico de ASan. Não introduza unsafe apenas para imitar UB.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código original: MIT. Dados originais: CC0 1.0. Documentação: CC BY 4.0.
As leituras em [references.md](../references.md) mantêm as licenças de origem.
