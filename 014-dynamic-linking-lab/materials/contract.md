# Contrato obrigatório

Ambiente: Linux x86-64, C11, ABI C, GCC ou Clang, binutils e Python 3.
Este contrato foi fixado antes do starter.

`library.h` declara `int oxide_add(int a, int b)` e `int oxide_square(int x)`.
As entradas usadas neste laboratório estão em [-100,100]; somas e quadrados cabem em int.
`liboxide.a` incorpora o componente no cliente `archive-client`; `liboxide.so` atende `shared-client`.
Ambos imprimem `7 25\n` e retornam 0. O primeiro ainda pode depender dinamicamente da libc;
static linking de um archive não significa produzir um executável inteiramente estático.

O participante implementa `dynamic.c`. CLI: `dynamic PATH SYMBOL now|lazy skip|call`.
PATH é um caminho explícito para uma biblioteca confiável, SYMBOL é uma função com assinatura
`int (int,int)`. `oxide_add` é a operação válida. `skip` abre e fecha sem buscar símbolo;
`call` busca o símbolo e o chama com (3,4), imprimindo seu resultado decimal e newline.
Sucesso retorna 0. CLI inválida retorna 2 com diagnóstico em stderr. Falha de dlopen retorna 3,
falha de dlsym retorna 4, falha de dlclose retorna 5. Diagnósticos controlados começam por
`open:`, `symbol:` ou `close:`, respectivamente, seguidos do diagnóstico disponível.
`skip` não imprime nada. Em qualquer erro, stdout fica vazio. Guarde o resultado da chamada e só o imprima
após dlclose bem-sucedido. Se dlsym falhar e dlclose também falhar, preserve o código 4
e o diagnóstico primário `symbol:`; acrescente um diagnóstico `close:` em outra linha.
O código 5 aplica-se ao fechamento que falha sem erro primário anterior.

Use RTLD_LOCAL e RTLD_NOW ou RTLD_LAZY conforme a CLI. Limpe dlerror antes de dlsym,
consulte-o depois e só chame o ponteiro se não houver erro. Feche cada handle aberto exatamente
uma vez em caminhos controlados, incluindo símbolo ausente; não use o ponteiro após dlclose.
A conversão entre endereço de dlsym e ponteiro de função segue POSIX, além do C11.
Não tente inferir compatibilidade de assinatura pelo nome: chamar assinatura incompatível pode
causar comportamento indefinido. A fixture de API alterada apenas renomeia o símbolo.

`broken.so` é um alvo de teste MIT que referencia uma função ausente. Em loaders com lazy binding,
now/skip deve falhar na abertura e lazy/skip pode funcionar; lazy/call pode encerrar o processo
pelo loader. Esse último status e texto são observações, não códigos controlados da CLI.
LD_BIND_NOW, linker e libc podem antecipar a resolução; registre diferenças sem forçar o resultado.
Não altere ld.so.conf, cache do loader ou bibliotecas do sistema.
