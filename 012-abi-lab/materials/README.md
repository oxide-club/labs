# Materiais de investigação

`calls.c` contém funções C completas para observar 1, 3, 6 e 8 argumentos.
`arithmetic.h` fixa assinaturas compartilhadas. `arithmetic.S` é o starter incompleto.
`vectors.json` contém fixtures originais CC0 1.0, com inteiros decimais sem perda de precisão em Python.
Não leia esse JSON com ferramentas que convertam inteiros grandes em ponto flutuante.

Os checks acrescentam oito vetores de posição única e 32 vetores determinísticos,
calculados com inteiros Python e redução módulo 2^64. Isso evita depender apenas da referência C.
`checks/probe.S` é instrumentação completa: chama a função com sentinels nos seis
registradores callee-saved e fornece alignment_probe, que destrói registradores caller-saved.
O check não compara instruções, endereços nem padrões de prólogo.
Não altere a instrumentação ou os vetores para encobrir uma implementação incorreta.

## Linguagens e ambiente

**Linguagem de referência:** C + GNU assembly.

**Linguagens aceitas:** C e assembly no núcleo; Rust como extensão FFI.

**Linguagens recomendadas:** Rust para extensão FFI.

**Restrições técnicas e plataforma:** Linux x86-64, System V AMD64 LP64, alinhamento e registradores preservados.

**Tipo de equivalência:** apenas comparativa para a extensão FFI.

### Contrato independente da linguagem

Preserve arithmetic8, alignment_probe e object files separados. Aritmética uint64 é módulo 2^64; em Rust use operações wrapping quando necessário. O harness de registradores e alinhamento não pode ser substituído por comparação de stdout.

O contrato original, suas APIs, fixtures e critérios continuam válidos para a
versão existente. As instruções que nomeiam seu arquivo ou compilador descrevem
essa versão. Para outra linguagem, entregue o mesmo raciocínio, os casos e as
observações do mecanismo, mais o mapeamento de tipos, erros e lifetime.
Não altere fixtures para acomodar diferenças da implementação.

**Variantes oficiais adicionais:** nenhuma. Os materiais da linguagem de referência continuam disponíveis.

Build e rejeição esperada do starter verificam a preparação, não a conclusão do exercício. Linguagem aceita sem starter não implica manutenção ou CI.

## Licenças

Código original: MIT. Traces e dados de teste originais: CC0 1.0.
Documentação: CC BY 4.0. Materiais de terceiros conservam seus avisos próprios.
Consulte os avisos e os textos das licenças incluídos no pacote.
