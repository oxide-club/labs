# Referências orientadas

Consultadas em 25/10/2026. Os links de código usam versões nomeadas; não dependem de `master`.

- [GNU binutils: readelf](https://sourceware.org/binutils/docs/binutils/readelf.html): opções `-S`, `-l`, `-s` e `-r` para seções, segmentos, símbolos e relocations. Compare a organização de arquivo com os dados necessários ao carregamento. Pergunta: qual tabela descreve `LOAD`?
- [Linux v6.12: fs/binfmt_elf.c](https://github.com/torvalds/linux/blob/v6.12/fs/binfmt_elf.c): `load_elf_binary` interpreta ELF e organiza carregamento inicial no kernel. Observe `PT_LOAD`, `PT_INTERP` e `load_elf_interp`. O laboratório observa esse caminho; não implementa um loader. Pergunta: como a entrada muda quando há interpretador?
- [musl v1.2.5: ldso/dynlink.c](https://github.com/ifduyue/musl/blob/v1.2.5/ldso/dynlink.c): dynamic loader em espaço de usuário. Observe carregamento de bibliotecas, busca de símbolos e relocations. O sistema local pode usar outra libc; não suponha que o trace executou musl. Pergunta: quais tarefas exigem informações ausentes em um object file isolado?

Os arquivos e mecanismos foram consultados pela interface web. As tags fixam versões de leitura, mas não equivalem a um SHA imutável; resolver commits permanece uma melhoria de rastreabilidade. Nenhum código dessas fontes foi incorporado aos materiais.
