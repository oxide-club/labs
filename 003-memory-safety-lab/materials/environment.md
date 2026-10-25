# Ambiente descartável Alpine com Clang

Use Linux, GNU Make, Python 3.10+, `qemu-system-x86_64` e `bsdtar` no host.
Reserve cerca de 1 GiB de disco para os insumos e 2 GiB de RAM por VM.
KVM é usado quando acessível; QEMU pode usar TCG, mais lento.
Nenhum pacote é instalado globalmente no host.

```sh
make env-setup
make test
make run
make env-shell
make env-clean
```

`env-setup` baixa Alpine virt 3.22.7 x86-64 e os pacotes fixados no manifesto
`environment.json`. Verifica SHA256 de cada arquivo e extrai kernel e initramfs
somente da imagem verificada. Clang, compiler-rt e LLVM são versão 20.1.8.
Todos os insumos ficam em `.lab-env/`, fora do pacote distribuído e do Git.
Não há consulta a versões "latest" nem resolução de dependências pela rede
quando um experimento executa. Se um pacote fixado deixar de estar disponível,
a preparação falha; não substitui silenciosamente sua versão.

Para usar uma imagem já baixada:

```sh
make env-setup ENV_ISO=/caminho/alpine-virt-3.22.7-x86_64.iso
```

Para reaproveitar todos os insumos de outro laboratório, informe seu diretório
`.lab-env/` por `ENV_ASSETS`. O diretório é somente fonte de leitura e todos os
arquivos são verificados antes da cópia. Arquivos ausentes são baixados:

```sh
make env-setup ENV_ASSETS=/caminho/outro-laboratorio/.lab-env
```

`test`, `run` e `verify-preparation` iniciam uma VM nova sem placa de rede.
O sistema vive na RAM e instala os APKs verificados offline a cada boot.
Isso evita manter um disco de trabalho mutável, mas acrescenta tempo ao boot.
As assinaturas dos APKs continuam verificadas pelas chaves da imagem Alpine.
A VM usa Clang por padrão e inclui o simbolizador LLVM para função e linha.

Somente arquivos textuais distribuídos da atividade entram na VM. Não são
compartilhados home, credenciais, sockets ou diretórios pais. A entrada é
somente leitura. A única pasta gravável compartilhada é um diretório novo de
`results/`. O exercício roda como usuário `lab`, sem privilégios.
Digite `confirmed` no console do guest antes da execução. A variável
`OXIDE_DISPOSABLE_VM` só é definida nessa sessão; não a configure no host.

Ao terminar, a VM é desligada e seu estado em RAM desaparece. Evidências,
versões, stdout, stderr e status ficam em `results/vm-*/`. Falhas do exercício
continuam sendo falhas do Make. Falta de status ou interrupção não vira sucesso.
`env-clean` remove apenas os insumos conhecidos e preserva resultados e arquivos
próprios. Ele recusa executar enquanto outra sessão usa o mesmo ambiente.
`clean` continua limitado aos artefatos de build do laboratório.

`env-shell` abre um shell do usuário `lab`. Use os mesmos comandos Make dentro
dele e termine com `exit`. Alterações feitas nos fontes do guest são descartadas:
edite no host e inicie nova sessão. Copie suas evidências para `results/`.
Os comandos originais documentados continuam disponíveis em uma VM preparada
manualmente. O laboratório 016 mantém todas as guardas e a confirmação explícita.

Se a receita ou algum insumo mudar, repita `env-setup`. Em erro de checksum,
examine a mensagem e use `env-clean` antes de baixar novamente. Não use arquivos
alterados nem desative a verificação. Consulte o log `install.log` da sessão se
um APK não puder ser instalado.

Fontes: [Alpine 3.22](https://dl-cdn.alpinelinux.org/alpine/v3.22/),
[pacotes compiler-rt](https://pkgs.alpinelinux.org/package/v3.22/main/x86_64/compiler-rt),
[QEMU](https://www.qemu.org/docs/master/system/invocation.html).

Hashes fixam insumos, não tempos, PIDs ou endereços. O ambiente atende aos materiais
didáticos deste pacote; não é uma plataforma para binários adversariais arbitrários.
Atualizações exigem revisar imagem, pacotes e checks.
