# Laboratório de Segurança de Memória

Compare view, cópia e invalidação lógica. Leia o [enunciado](index.md) e registre
as hipóteses antes de executar os instrumentos completos.

```sh
python3 materials/experiments/compare.py /tmp/oxide-memory-comparison
```

Use um diretório novo. O runner preserva logs e metadados, com processos separados
e timeout. A coleta exige C11, Python 3 e ASan/LSan. Uma falha do sanitizador torna
a observação pendente; não a trate como ausência de defeito.

Siga o [guia dos materiais](materials/README.md) para as intervenções obrigatórias.
A correção antiga e a CLI de offsets continuam como [extensão opcional](materials/legacy.md).
Seus checks não são os critérios de conclusão da investigação atual.

Documentação: CC BY 4.0. Código: MIT. Dados originais: CC0-1.0.
