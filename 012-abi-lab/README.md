# Guia local — ABI e Calling Conventions

Leia [o enunciado](index.md). Os comandos partem deste diretório, em Linux x86-64:

```sh
python3 checks/check.py
CC=clang python3 checks/check.py
```

O starter compila, mas os checks retornam status 1: faltam cálculo e chamada ao probe.
Essa falha é esperada. O check compila em diretório temporário e remove seus artefatos.
Não há dependências Python externas. O timeout de execução é cinco segundos.
Leia [os materiais](materials/README.md) e siga [o experimento](experiments/calling.md).
Registre evidências no [modelo de relato](report-template.md), incluído a partir do modelo central.

Documentação original: CC BY 4.0. Código original: MIT. Fixtures originais: CC0 1.0.
Fontes externas mantêm suas licenças; não foram copiadas para o laboratório.
