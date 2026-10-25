# Materiais — Protocolos Binários

`protocol.py` contém a API, o objeto de mensagem e o transporte de diagnóstico.
Encoder, parser incremental, validação e EOF permanecem por implementar.
Não use bibliotecas que implementem framing por você.

[vectors.json](vectors.json) contém bytes externos em hexadecimal, campos esperados e códigos de erro.
Os valores foram definidos pelo contrato, sem chamar encode para produzi-los.
O vetor máximo registra explicitamente 4096 bytes `ab` e o comprimento big-endian `00001000`.
O vetor binary contém zero, `ff` e ASCII `41`: payload não exige UTF-8.
O campo license aplica CC0 1.0 aos dados originais.

[O contrato](../index.md) define tipos exatos, limites e precedência de validação.
[Os checks](../checks/check.py) usam esses bytes como oráculo e depois acrescentam roundtrip.
As partições exaustivas dos casos pequenos incluem divisões em três ou mais chunks.
Os prefixos próprios verificam EOF; chunks vazios entre fragmentos não encerram o fluxo.
O limite persistente e o número de cópias exigem revisão do código, além dos checks funcionais.

## Linguagens e ambiente

**Linguagem de referência:** Python.

**Linguagens aceitas:** Livre; por exemplo C, Rust, Go e Python.

**Linguagens recomendadas:** Rust, Go e Python.

**Restrições técnicas e plataforma:** Header de oito bytes; length uint32 big-endian até 4096; parsing incremental próprio.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve magic, versão, flags, bytes opacos, precedência de erros, mensagens concluídas antes da falha, EOF e estado terminal. Chunks até 65536 bytes e estado persistente até 4104 bytes. Em Go, errors e slices substituem exceções e bytes; a interface deve copiar dados retornados e não reter chunks. Tipos exatos Python não são requisitos do sistema de tipos Go.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variante oficial adicional:** [starter go](starter/go/README.md).

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
