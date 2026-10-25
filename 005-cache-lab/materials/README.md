# Materiais de Cache e Localidade

- `starter/cache.c`: código inicial em C. Ele compila, mas ainda não simula a cache.
- `inputs/trace-a.txt`: oito leituras para prever os resultados à mão.
- `inputs/trace-b.txt`: dezesseis leituras para verificar substituições.
- `../checks/check.py`: programa que verifica os contadores com entradas e resultados conhecidos.
- `../report-template.md`: instruções para registrar sua investigação.

Depois de extrair o pacote, abra um terminal no diretório do laboratório.
Execute os comandos abaixo.

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/starter/cache.c -o cache
python3 checks/check.py ./cache
```

O código inicial falha nas verificações até você implementar o simulador.
Use Python 3 para executar o programa de verificação.

Você também deve entregar um gerador dos percursos da matriz.
Use a linguagem de sua preferência para esse gerador.

## Linguagens e ambiente

**Linguagem de referência:** C11.

**Linguagens aceitas:** Livre; por exemplo C, Rust, Go e Python.

**Linguagens recomendadas:** Rust, Go e Python.

**Restrições técnicas e plataforma:** Endereços sintéticos de 64 bits, quatro linhas de 16 bytes, mapeamento direto.

**Tipo de equivalência:** equivalente ao núcleo.

### Contrato independente da linguagem

O contrato já é a CLI: stdin com traces, stdout hits=N misses=N evictions=N e status zero. Use o mesmo checks/check.py com qualquer executável ou wrapper. Preserve todos os 64 bits; não desreferencie endereços. Contadores representam contagens exatas; não adote wraparound silencioso. O contrato publicado cobre traces válidos e não fixa uma política para entradas malformadas.

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
