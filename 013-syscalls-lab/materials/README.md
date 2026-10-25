# Materiais

- [write_libc.c](starter/write_libc.c): exemplo completo de escrita com retomada.
- [write_syscall.c](starter/write_syscall.c): TODO do participante; ENOSYS é uma falha deliberada.
- [write_api.h](starter/write_api.h) e [driver.h](starter/driver.h): interface e CLI comuns.
- [contract.c](../checks/contract.c): retornos parciais, EINTR antes e depois de progresso parcial, EBADF inicial e após progresso, zero e entrada vazia.
- [cli.py](../checks/cli.py): observa status, stdout e stderr reais, com timeout.
- [Makefile](Makefile): compilação e verificação com `make -C materials check` na raiz do pacote.
- [expected.txt](expected.txt): seis bytes UTF-8/ASCII `oxide` mais LF, sem BOM; licença CC0-1.0.
- [trace.md](../experiments/trace.md): experimento real e comparação de assembly.

Execute a partir da raiz do pacote. Nenhum arquivo de outro laboratório é necessário.
A comparação de backend exige revisão da fonte: equivalência de saída sozinha não demonstra uso de SYS_write.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** C no contrato original; Rust e assembly x86-64 com adaptação explícita.

**Linguagens recomendadas:** Rust e assembly x86-64.

**Restrições técnicas e plataforma:** Linux x86-64; ABI syscall e distinção libc/kernel obrigatórias.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve write_all, retomada de EINTR, avanços parciais, EIO para retorno zero e bytes já escritos após falha. CLI permanece oxide\n e status publicados. Rust/assembly devem distinguir erro bruto negativo do kernel de -1/errno da libc; adaptar o backend testável, sem usar uma rotina write_all pronta.

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
