# Leituras orientadas

Consulta em 25/10/2026. As fontes abaixo foram abertas durante a preparação.
Elas sustentam a investigação; o [contrato local](materials/contract.md) define o exercício.

## Para começar

- [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/): leia Process API e introdução à segurança.
  Relacione criação de processos, privilégios e ativos que precisam de proteção.
- [PR_SET_CHILD_SUBREAPER](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html):
  acompanhe a adoção de órfãos. Por que o avô comum não pode executar reaping de qualquer neto?
- [getrlimit/setrlimit](https://man7.org/linux/man-pages/man2/getrlimit.2.html): compare
  RLIMIT_AS e RLIMIT_CPU e a diferença entre limite soft e hard.

## Para comparar mecanismos

- [namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html): identifique
  qual objeto cada tipo torna visível de maneira distinta e quais permissões são necessárias.
- [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html): leia controllers,
  delegação e memory/pids/cpu. Diferencie limite por processo de limite hierárquico agregado.
- [seccomp(2)](https://man7.org/linux/man-pages/man2/seccomp.2.html): leia requisitos
  de instalação, ações e diferenças entre modo estrito e filtros. Como uma política
  restringe syscalls sem decidir quais arquivos um file descriptor já aberto representa?
- [The Linux Programming Interface](https://www.man7.org/tlpi/): aprofundamento em
  sinais, file descriptors e credenciais; consulte também as man-pages para interfaces recentes.

## Código real: Bubblewrap

Leia [bubblewrap.c na revisão 9ca3b05ec787acfb4b17bed37db5719fa777834f](https://github.com/containers/bubblewrap/blob/9ca3b05ec787acfb4b17bed37db5719fa777834f/bubblewrap.c),
correspondente à versão 0.11.0. O [fonte bruto fixado](https://raw.githubusercontent.com/containers/bubblewrap/9ca3b05ec787acfb4b17bed37db5719fa777834f/bubblewrap.c)
foi conferido; a [revisão da versão](https://github.com/containers/bubblewrap/commit/9ca3b05ec787acfb4b17bed37db5719fa777834f)
permite reproduzir a leitura.

O arquivo prepara ambientes com namespaces, mounts, file descriptors e restrições Linux.
Observe `clone_flags`, `setup_newroot`, `close_ops_fd` e o tratamento de `opt_seccomp_fd`.
Compare a ordem de preparação e abandono de privilégios com as invariantes do seu
supervisor. Esse programa de produção tem contexto e responsabilidades muito maiores
que o exercício; conhecer seu código não confere essas propriedades ao starter.

**Pergunta de leitura:** qual etapa muda a visão do filesystem, qual fecha um file descriptor
herdado e qual instala uma política de syscall? Que risco permanece se uma delas faltar?

Nenhum código do Bubblewrap foi copiado para o pacote. O fonte consultado declara
LGPL-2.0-or-later e conserva sua licença. A API do GitHub para resolver a tag não abriu
na ferramenta de consulta; a página da versão e o fonte no commit acima foram acessíveis.
