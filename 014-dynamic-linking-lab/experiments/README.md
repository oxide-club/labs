# Falhas e momento da resolução

Execute após implementar `dynamic.c`, da raiz do pacote. Preveja, observe e explique cada caso.
Registre stdout, stderr e status; o texto do loader varia entre sistemas.

```sh
materials/build/dynamic ./materials/build/liboxide.so oxide_add now call
materials/build/dynamic ./materials/build/absent.so oxide_add now call
materials/build/dynamic ./materials/build/renamed.so oxide_add now call
materials/build/dynamic ./materials/build/broken.so oxide_add now skip
materials/build/dynamic ./materials/build/broken.so oxide_add lazy skip
materials/build/dynamic ./materials/build/broken.so oxide_add lazy call
```

O resultado válido é 7. Biblioteca ausente retorna 3; símbolo renomeado retorna 4.
`broken.c` deixa uma referência de função indefinida. NOW pode detectá-la ao abrir;
LAZY pode adiá-la até chamar a função, quando o loader pode encerrar o processo.
Nem todo loader implementa esse adiamento. Registre `getconf GNU_LIBC_VERSION` quando disponível,
`cc --version`, `ld --version` e a presença de LD_BIND_NOW ou LD_PRELOAD antes de interpretar.
Não exporte essas variáveis para a sessão inteira. Compare opcionalmente uma única execução
com `env LD_BIND_NOW=1` e explique o alcance da variável.

Para observar uma dependência ausente antes de main, copie apenas o cliente para um diretório
local temporário, sem mover a biblioteca original:

```sh
mkdir -p materials/build/isolated
cp materials/build/shared-client materials/build/isolated/
materials/build/isolated/shared-client
```

O loader deve denunciar a dependência local ausente, salvo se houver outra liboxide.so em seu
ambiente. Compare com `archive-client`. Explique por que essa falha ocorre antes da CLI.
Inspecione `readelf -Ws materials/build/broken.so` e encontre `oxide_missing` indefinido.
Não altere o host para obter um resultado previsto.
