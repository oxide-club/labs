# File descriptors, progresso e reaping

Antes de implementar, preencha a tabela. `r` e `w` são os file descriptors retornados pelo pipe. Descreva também o caso em que um deles já coincide com stdin ou stdout; um fechamento incondicional após `dup2(fd, fd)` pode fechar o destino.

| Momento/processo | stdin | stdout | stderr | Cópia r | Cópia w | PID a esperar |
| --- | --- | --- | --- | --- | --- | --- |
| Pai após pipe | prever | prever | herdado | prever | prever | nenhum ainda |
| Esquerda antes de execvp | prever | prever | herdado | prever | prever | não se aplica |
| Direita antes de execvp | prever | prever | herdado | prever | prever | não se aplica |
| Pai antes de waitpid | herdado | herdado | herdado | prever | prever | prever |
| Falha no segundo fork | herdado | herdado | herdado | prever | prever | prever |

Preveja e execute os casos abaixo depois da implementação. Registre stdout e `$?` separadamente.

```sh
./build/oxrun run -- printf '%s\n' 'a b'
./build/oxrun pipe -- printf 'abc\n' ::: wc -c
./build/oxrun pipe -- dd if=/dev/zero bs=1024 count=1024 ::: wc -c
./build/oxrun pipe -- true ::: cat
./build/oxrun pipe -- ./build/probe ::: true
./build/oxrun pipe -- true ::: ./build/probe
```

Resultados exigidos: `a b` e status 0; contagens 4 e 1048576 com status 0; EOF sem bytes com status 0; status 0 e 7 nos dois últimos casos. Estatísticas de `dd` permanecem em stderr.

Explique: qual escritor esquecido impede EOF? Por que o pipeline deve iniciar ambos os filhos antes de esperar? Por que o status da direita não dispensa esperar a esquerda? `execvp` altera o PID? Como distinguir filho terminado de filho cujo reaping já ocorreu?

Se usar `strace -f -e trace=process,desc`, registre a criação, duplicação, fechamento e espera observados. Não fixe números de PID. Não apresente ausência momentânea em `ps` como prova de reaping pelo pai.
