# Materiais

Execute comandos da raiz do pacote. `make -C materials` grava somente em `materials/build/`.
`library.h` e `library.c` definem duas operações; `client.c` é compilado contra archive e `.so`.
O Makefile usa PIC no objeto compartilhado e RUNPATH relativo a `$ORIGIN` no cliente.
Esse caminho aponta para o diretório do executável, não para o diretório corrente.

Leia [contract.md](contract.md) antes de completar [dynamic.c](dynamic.c).
A implementação de `dlopen`/`dlsym` é o trabalho do participante. Os exemplos de biblioteca
não constituem uma implementação desse mecanismo. `-ldl` mantém compatibilidade com glibc antiga.

```sh
materials/build/archive-client
materials/build/shared-client
python3 checks/check.py
```

Inspecione os ELF conforme o enunciado. Não compare tamanhos como prova de desempenho;
registre flags, versão do compilador e libc. Os checks têm timeout de cinco segundos por execução.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** C no núcleo C/ELF; Rust e C++ como extensão de interoperabilidade.

**Linguagens recomendadas:** Rust e C++.

**Restrições técnicas e plataforma:** Linux x86-64/ELF, dlopen/dlsym, PIC, símbolos e lifetime do handle.

**Tipo de equivalência:** apenas comparativa para extensões.

### Contrato independente da linguagem

Preserve library.h, clientes, library.c e dynamic.c. Bibliotecas de outra linguagem devem declarar ABI C/exportação e regras de ownership. Uma biblioteca carregada não pode ser descarregada enquanto funções ou dados ainda são usados. A extensão não substitui a investigação C/ELF.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

Os checks incluem uma biblioteca compartilhada com destrutor e um wrapper de `dlclose`: observam fechamento em call/skip/símbolo ausente, ordem antes da impressão e precedência de erro quando o fechamento falha. Ambos são fixtures, sem implementar o cliente.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
