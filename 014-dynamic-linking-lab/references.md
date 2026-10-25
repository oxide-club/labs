# Referências orientadas

Consulta em 25/10/2026. As páginas abaixo foram abertas e seu mecanismo foi conferido.

- [Linux man-pages: dlopen](https://man7.org/linux/man-pages/man3/dlopen.3.html): leia flags,
  busca de caminhos e retorno. LAZY aplica adiamento a referências de funções; variáveis
  precisam de resolução imediata. Use essa distinção para explicar a fixture.
- [Linux man-pages: dlsym](https://man7.org/linux/man-pages/man3/dlsym.3.html): leia o protocolo
  com dlerror. O exemplo de conversão POSIX está em dlopen(3). Um endereço NULL isolado não basta para diagnosticar erro.
- [musl v1.2.5, ldso/dynlink.c](https://github.com/ifduyue/musl/blob/v1.2.5/ldso/dynlink.c):
  código de produção em C, revisão por tag (não SHA). Arquivo consultado diretamente na revisão indicada.
  Após o núcleo, localize `do_relocs`, `dlopen` e `__dlsym`; acompanhe busca e resolução.
  Há locks, TLS e dependências que não pertencem ao cliente didático. Pergunta: onde o loader
  transforma uma referência simbólica em endereço e como trata erro durante abertura?

Leituras curriculares complementares, sem conferência de conteúdo integral nesta preparação:
[Zhirkov, capítulo 15](https://link.springer.com/book/10.1007/978-1-4842-2403-8) e
[CS:APP, capítulo 7](https://csapp.cs.cmu.edu/3e/). A conclusão do núcleo não depende de acesso aos livros.

O exemplo POSIX de conversão do resultado de `dlsym` para ponteiro de função está em [dlopen(3)](https://man7.org/linux/man-pages/man3/dlopen.3.html), na seção EXAMPLES. Uma conversão direta pode ser rejeitada por `-Wpedantic` em C ISO; examine o idiom POSIX apresentado nessa seção.
