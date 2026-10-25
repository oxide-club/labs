# Materiais da arena

**Material histórico:** atividade consolidada no [desafio 017-arena](https://oxideclub.dev/desafios/017-arena/).
As APIs abaixo documentam a versão anterior; não são requisitos adicionais do desafio.


Execute os comandos abaixo na raiz deste laboratório, onde está `index.md`.
Requisitos: compilador C11, Linux e GNU ld para o check com `--wrap`.
Binários ficam em `/tmp`, fora dos materiais distribuídos.

- `starter/arena.h`: API obrigatória, preservada do Anexo A.
- `starter/arena.c`: corpos incompletos; complete sem mudar as assinaturas.
- `checks/tests.c`: casos públicos e invariantes; não contém alocador de referência.
- `checks/fail_malloc.c`: injeta falha determinística de `malloc` via linker.
- `fixtures/requests.csv`: vetores normativos de continuidade e limite exato.
  Cada cenário começa com uma arena nova; cada linha continua o cenário anterior.
  O comentário inicial informa a licença. Os checks contêm valores independentes.
- `experiments/layout.c`: consulta tamanhos, alinhamentos e resto do endereço da base;
  não calcula a posição de allocations na arena.

## Compilar e observar

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 materials/experiments/layout.c -o /tmp/arena-layout
/tmp/arena-layout
```

Registre a saída e preveja o offset de `long double` depois de um byte.
Valores de tamanho e alinhamento dependem do ambiente; não copie uma medição alheia.

## Verificar o contrato

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 -I materials/starter materials/starter/arena.c materials/checks/tests.c -o /tmp/arena-tests
/tmp/arena-tests
cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 -I materials/starter materials/starter/arena.c materials/checks/fail_malloc.c -Wl,--wrap=malloc -o /tmp/arena-fail-malloc
/tmp/arena-fail-malloc
```

O check principal retorna 1 com o starter; ele só executa casos de allocation após
uma inicialização bem-sucedida. Depois da implementação, ambos devem retornar 0.
O check isolado de falha pode passar com o starter: isso não valida o núcleo.
`--wrap=malloc` evita depender da política de overcommit ou de um pedido gigante.
Não execute `alloc` sobre estrutura zerada: essa entrada está fora do contrato.

Para diagnóstico adicional, substitua `-O2` por
`-O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all` no primeiro comando.
Não dereferencie referências anteriores ao reset para tentar provar sua invalidação:
a regra é contratual e o armazenamento continua reservado.

## Relato

Use o `report-template.md` incluído no pacote. No repositório, a fonte é
[o modelo compartilhado](../report-template.md). Registre hipótese,
observação, explicação, comandos e limitações.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** Livre sob gerenciamento explícito; por exemplo C, Rust e C++.

**Linguagens recomendadas:** Rust e C++.

**Restrições técnicas e plataforma:** Região real, alinhamento, ponteiros, lifetime e política própria de allocation.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve capacidade, used, padding, ausência de overlap, reset e falha sem consumir espaço. Declare a largura de size_t/usize e verifique overflow antes de somar. Outra API deve explicitar o alinhamento máximo do ambiente; para comparar com C, use o mesmo limite de max_align_t. Uma Vec por objeto ou allocator pronto não satisfaz o mecanismo. Containers podem reservar uma região auxiliar, mas não decidir allocations individuais nem esconder validade após reset.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código MIT, fixtures CC0-1.0,
documentação CC BY 4.0.
