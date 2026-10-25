# VM de referência — revisão 2

A VM usa Linux x86-64 e executa as sondas como usuário comum. Ela complementa o host Omarchy usado na primeira preparação. Não substitua registros da VM por registros do host.

## Configuração fixada

| Componente | Configuração |
| --- | --- |
| Distribuição | Alpine Linux virt 3.22.7, x86-64 |
| ISO | `alpine-virt-3.22.7-x86_64.iso` |
| SHA-256 da ISO | `c345ec65055908734523e03e81137a2e2f82f0094eb2b6e99bc6e07a7d2a0556` |
| Kernel | `6.12.114-0-virt` |
| libc | musl `1.2.5-r13` |
| Compilador | GCC `14.2.0-r6` |
| Binutils | `2.44-r3` |
| Python | `3.12.15-r0` |
| strace | `6.13-r0` |
| Virtualização observada | QEMU 11.1.2, máquina q35, TCG, CPU `max`, 2 vCPUs |
| Memória | 2048 MiB |
| Disco | Sistema efêmero em RAM, ISO somente leitura; nenhum disco do host |
| Rede | Desativada (`-nic none`) |
| Usuário do experimento | `lab`, UID 1000, sem privilégios |

[vm-assets.json](vm-assets.json) fixa URLs oficiais e SHA-256 da ISO e dos pacotes usados. Os pacotes adicionais incluem dependências de build e Python. Não são redistribuídos pelo laboratório. A instalação respeita as assinaturas APK; não use `--allow-untrusted`.

## Preparar os arquivos

No host, obtenha a ISO e os APKs listados no manifesto. Confira SHA-256 antes de iniciar. Mantenha-os num diretório próprio `assets/`; coloque os APKs em `share/apks/`. Faça uma cópia do pacote do participante em `share/package/`. Não compartilhe o diretório pessoal, o repositório inteiro ou o socket do sistema com a VM.

Extraia `boot/vmlinuz-virt` e `boot/initramfs-virt` da ISO com uma ferramenta de leitura de ISO, como `bsdtar`:

```sh
mkdir boot
bsdtar -xf assets/alpine-virt-3.22.7-x86_64.iso -C boot boot/vmlinuz-virt boot/initramfs-virt
```

Inicie uma VM própria. Use caminhos absolutos no argumento `path=` de `-virtfs`:

```sh
qemu-system-x86_64 -machine q35,accel=tcg -cpu max -m 2048 -smp 2 \
  -display none -monitor none -serial stdio -no-reboot \
  -kernel boot/boot/vmlinuz-virt -initrd boot/boot/initramfs-virt \
  -append 'console=ttyS0 modules=loop,squashfs,sd-mod,usb-storage quiet' \
  -cdrom assets/alpine-virt-3.22.7-x86_64.iso -nic none \
  -virtfs local,path=/CAMINHO/ABSOLUTO/share,mount_tag=inputs,security_model=none,readonly=on
```

O login inicial `root` pertence somente à VM descartável. Use-o para instalar ferramentas em RAM e criar o usuário; não execute as sondas como root.

```sh
mkdir -p /mnt/inputs
mount -t 9p -o trans=virtio,version=9p2000.L,ro inputs /mnt/inputs
apk add --no-network --force-non-repository /mnt/inputs/apks/*.apk
adduser -D -u 1000 lab
mkdir -p /home/lab/work
cp -R /mnt/inputs/package /home/lab/work/package
chown -R lab:lab /home/lab/work
su lab
cd /home/lab/work/package
make -C materials/starter/c
make -C materials/starter/c audit
python3 checks/check.py materials/starter/c/pageprobe --audit-out /tmp/pageprobe-audit
```

`--force-non-repository` permite a instalação local efêmera, perdida ao desligar; não desativa a verificação de assinatura. O starter compila e deve ser rejeitado com status 1, pois o supervisor está incompleto. Depois de implementar, o mesmo comando deve retornar 0, incluindo a auditoria independente. Use novo diretório de saída a cada execução.

Registre `id`, `uname -a`, `/etc/alpine-release`, `cc --version`, `objdump --version`, `python3 --version`, `strace --version` e `apk info -vv`. Preserve stdout, stderr, código de saída, `all.strace` e `all.stdout`. Uma montagem de saída separada, restrita a uma pasta vazia própria, pode preservar esses arquivos no host. A preparação automatizada usou exatamente esse arranjo, além de uma configuração de boot efêmera para automatizar os comandos.

## Particularidade de mprotect

Na VM observada, o wrapper `mprotect` da musl alinhou o endereço antes de chamar o kernel. O controle de endereço inválido usa `syscall(SYS_mprotect, endereço_desalinhado, tamanho, proteção)`, com `<sys/syscall.h>`, para testar a syscall Linux diretamente. O retorno observado foi -1/EINVAL. Registre essa escolha; uma função da libc e a syscall não são intercambiáveis para todas as entradas.

As demais transições usam endereços alinhados. Não mude a política global de memória, a personalidade do processo ou sysctls para obter os resultados. O tamanho de página continua sendo consultado pelo supervisor; 4096 bytes foi a observação desta VM.

## Evidência e limites

A preparação registra separadamente o primeiro teste, que detectou o ajuste da musl, e a repetição com syscall explícita. O protocolo exige build, check completo e auditoria na VM; boot bem-sucedido sozinho não aprova o ambiente.

A configuração é reproduzível pelos artefatos fixados; não promete PIDs, endereços nem latência iguais. TCG pode alterar duração. A tolerância operacional do laboratório continua valendo; uma execução que a exceda exige diagnóstico, sem converter timeout em SIGSEGV. Piloto com participante e aprovação humana de publicação continuam pendentes.
