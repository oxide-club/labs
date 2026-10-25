# Compilação e Execução

Leia o [enunciado](index.md) e o [guia dos materiais](materials/README.md).
O código auxiliar está completo; a entrega é uma investigação com evidências anotadas.

```sh
cd materials
make
make check
make observe
```

Os checks devem retornar 0. Os dois erros de linking são esperados e verificados pelos checks.
`make observe` informa quando falta `strace`; não trate coleta parcial como conclusão integral.
Use o [modelo central de relato](report-template.md). No pacote, use o modelo incluído na raiz.

Documentação original: CC BY 4.0. Código original: MIT. Dados originais: CC0 1.0.
Os fontes externos são apenas referências; não foram copiados para o pacote.
