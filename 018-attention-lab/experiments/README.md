# Memória da matriz explícita

Execute da raiz do laboratório. Antes de medir, registre a hipótese para o
quociente de memória quando N dobra, mantendo d_k=8 e d_v=4.

## Previsão teórica

```bash
python3 experiments/memory.py --theory > /tmp/attention-theory.csv
```

O modo teórico funciona no starter. Produz N=16,32,64,128,256, `kind=theory`,
contagem `N*N`, bytes densos de scores `8*N*N` e bytes densos de scores mais
probabilidades `16*N*N`. As duas últimas colunas modelam números binary64
contíguos. Elas excluem headers, referências e demais objetos Python.
Headers são os metadados associados às listas e aos objetos numéricos.
Ao dobrar N, essas quantidades quadruplicam por definição, sem executar attention.

## Observação da implementação

```bash
python3 checks/check.py
python3 experiments/memory.py --measure > /tmp/attention-measured.csv
python3 experiments/memory.py --measure --causal > /tmp/attention-causal.csv
```

O modo de medição executa todos os checks públicos novamente em um subprocesso,
com limite de 60 segundos. Se houver falha ou timeout, retorna status 1 e não
emite CSV. No starter, esse é o resultado esperado. Use
`--candidate /caminho/attention.py` para uma variante compatível.

Uma allocation reserva memória para um objeto. O experimento gera entradas
determinísticas antes de rastrear allocations, faz
um aquecimento por N e executa três repetições. Cada repetição chama attention
inteira, mantendo o resultado vivo até consultar `tracemalloc`:

| Coluna | Escopo |
| --- | --- |
| `traced_retained_bytes` | Allocations Python ainda vivas ao fim da chamada |
| `traced_peak_bytes` | Pico de allocations Python durante a chamada |
| `traced_elapsed_seconds` | Tempo de parede da chamada com rastreamento ativo |
| `python`, `implementation`, `platform` | Ambiente efetivamente usado |
| `n`, `d_k`, `d_v`, `causal`, `repeat` | Configuração da amostra |

As medições incluem resultados S/P/O, validação e intermediários temporários
conforme a implementação; excluem entradas já criadas, importação, checks e
aquecimento. O rastreamento altera o tempo: não use essa coluna como benchmark
sem instrumentação. A medição não equivale a RSS, memória total do processo,
memória GPU ou contagem exclusiva de bytes de S/P. A coleta de lixo ocorre antes
de cada amostra. Não há valor mínimo ou razão temporal exigida.

Para uma investigação curta, use `--sizes 16,32,64 --repeats 3`. Cada N deve ficar
entre 1 e 256; repetições entre 1 e 20. CSV só é publicado após terminar todas
as chamadas, para que uma falha posterior não deixe amostras parciais aparentando sucesso.

## Interpretação e entrega

Entregue os três CSV, versão do Python, processador, comandos e código medido.
Compare a mediana e a faixa das repetições. Calcule razões entre N e 2N e
explique divergências em relação ao modelo denso: listas, objetos numéricos,
referências compartilhadas, validação e temporários alteram os custos observados.
Zerar posições futuras não reduz a forma N × N no núcleo obrigatório.

Os testes de suporte conferem a instrumentação com uma allocation controlada,
mas não são medições de attention. A preparação do pacote não fornece resultados
de desempenho de uma implementação central que ainda deve ser escrita.

Na interpretação de memória em CPython, compare `sys.getsizeof(0.0)` com o tamanho de uma referência: em uma plataforma de 64 bits, um float de 24 B mais uma referência de 8 B explica aproximadamente 32 B por elemento, contra 8 B do modelo denso. Meça no seu ambiente.
