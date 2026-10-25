# Laboratório de Engenharia Reversa

Reconstrua a decisão de um executável usando comparações e fluxo de controle.
Leia o [enunciado](index.md), siga o [guia dos materiais](materials/README.md) e
registre a investigação no [modelo de relato](report-template.md).

O alvo está completo. O fonte original foi renomeado de `porta.c` para `gate.c`,
sem alterar mensagens ou comparações. Reserve sua leitura para o confronto final.
Ele acompanha o pacote para permitir o build; não há promessa de sigilo.

Início rápido, a partir deste diretório:

```sh
python3 materials/experiments/prepare.py /tmp/oxide-reverse-lab
python3 materials/checks/check.py /tmp/oxide-reverse-lab/gate-O0
```

Os seis checks públicos devem passar. O status 0 depende da entrada que você
deduzir e verificar depois. Consulte as [referências orientadas](references.md).

Código original: MIT. Documentação: CC BY 4.0. Dados de teste originais: CC0 1.0.
