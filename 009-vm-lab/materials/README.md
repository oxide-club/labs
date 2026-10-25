# Materiais da VM

`vm.py` contém somente a assinatura que você deve implementar.
`expression.txt` calcula uma expressão; `branch.txt` contém um salto condicional e um salto incondicional;
`loop.txt` decrementa uma variável até zero. `bad-opcode.txt`, `bad-jump.txt` e `underflow.txt` cobrem três falhas distintas.
`cases.json` guarda resultados e traces calculados independentemente do starter. Os checks também geram entradas de fronteira.
Leia o contrato em [index.md](../index.md) antes de editar o starter. Arquivos .txt e .json são dados CC0 1.0.

## Linguagens e ambiente

**Linguagem de referência:** Python.

**Linguagens aceitas:** Livre; por exemplo C, Rust, Go e Python.

**Linguagens recomendadas:** Rust, Go e Python.

**Restrições técnicas e plataforma:** ISA textual publicada; int32 com sinal; validação integral e dispatch próprio.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve stack de 32 valores, oito variáveis, PC, budget, trace e códigos de erro. ADD/SUB fora de int32 falham sem consumir operandos; não use wraparound. O formato atual é texto, não bytecode binário: outro encoding é extensão. A API Python continua disponível; o adaptador Rust apenas transporta fonte e resultado para os mesmos checks.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variante oficial adicional:** [starter rust](starter/rust/README.md).

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
