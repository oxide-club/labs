# Materiais e verificações

O [contrato](contract.md) é normativo. O [starter](attention.py) expõe as três
funções públicas e deixa o mecanismo central em TODO. Nenhuma função de attention
completa é distribuída como oráculo.

| Arquivo | Papel |
| --- | --- |
| `attention.py` | Implementação do participante: validação e aritmética explícita |
| `fixtures/cases.json` | Cinco casos autorais CC0 com resultados independentes |
| `fixtures/README.md` | Derivações escalares e origem dos valores |
| `../checks/check.py` | Checks de intermediários, estabilidade, limites e causalidade |
| `../checks/verify_fixtures.py` | Conferência dos cinco casos fechados com Decimal |
| `../checks/test_support.py` | Verificação de comparação numérica e suporte experimental |
| `../experiments/memory.py` | Contagem teórica ou medição de uma implementação verificada |

Execute a partir da raiz do laboratório:

```bash
python3 checks/verify_fixtures.py
python3 checks/test_support.py
python3 checks/check.py
```

A conferência de fixtures não importa `attention.py`. Ela deve passar antes e
depois da implementação. Seus dois testes conferem os cinco casos e rejeitam
vetores com raiz quadrada truncada. O check público testa sete grupos de comportamento;
subcasos informam a entrada que falhou. No starter, os erros `NotImplementedError`
são esperados. Não são uma aprovação do trabalho do participante.

Os checks rejeitam formas erradas, números não finitos, probabilidades incorretas,
limites excedidos e `bool` no lugar de números. Verificam N=1/N=256,
d_k=1/d_k=64, d_v=1/d_v=64 e valores nos limites. A propriedade causal compara
o prefixo antes e depois de alterar entradas posteriores e com a sequência truncada.
Ela complementa os valores conhecidos; uma saída sempre zero não passa os fixtures.

Não use o diretório `checks` como biblioteca da implementação. Escreva helpers
de produto matricial e transposição no próprio `attention.py`, para que variantes
continuem independentes. Veja o [roteiro experimental](../experiments/README.md)
apenas depois de atender ao contrato e use o [modelo de relato](../report-template.md).

## Linguagens e ambiente

**Linguagem de referência:** Python.

**Linguagens aceitas:** Livre; por exemplo C, Rust, C++ e Python.

**Linguagens recomendadas:** Rust, C++ e Python.

**Restrições técnicas e plataforma:** Binary64; produtos, transposição, softmax estável e causal mask próprios; sem framework central.

**Tipo de equivalência:** equivalente sob contrato adaptado.

### Contrato independente da linguagem

Preserve os limites e erros de materials/contract.md, scores e probabilidades observáveis. Tolerâncias relativa 1e-9 e absoluta 1e-12, soma de probabilidades a 1e-12 de 1 e zeros mascarados exatos. Não arredonde intermediários; declare arredondamento binary64 do ambiente. Retornos devem ter ownership independente. Compare memória densa com objetos/runtime; tracemalloc não é medição portável de RSS.

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
