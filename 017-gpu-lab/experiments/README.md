# Experiências e análise

Antes de medir, execute os checks GPU. `measure.py` repete essa exigência e interrompe se houver falha.
O CSV de entrada descreve três conjuntos determinísticos; não contém tempos.
Nenhum resultado GPU acompanha este pacote.

A partir da raiz do laboratório, após implementar:

```sh
nvcc --version
nvidia-smi
python3 experiments/measure.py > /tmp/gpu-results.csv
```

Registre sistema, GPU, driver, runtime exibido pelo runner, compilador e flags.
O roteiro usa 64, 128, 256 e 512 threads por bloco, 10 execuções por combinação e aquecimento em cada processo.
Calcule mediana e dispersão de cada coluna, mantendo os dados brutos.
O total exclui contexto e allocations do runner: não o descreva como tempo de inicialização de um processo.
Para comparar CPU, meça separadamente apenas os loops de soma e reduction, sem geração nem impressão, e documente esse escopo.
A duração do CLI CPU inclui impressão de milhões de valores e não é uma comparação válida do cálculo.

**Prever:** qual tamanho terá maior proporção de custo de transferência e kernel launch?
**Observar:** identifique uma amostra real em que esse custo seja relevante.
**Explicar:** relacione-a à quantidade de bytes e operações, sem concluir sobre todas as GPUs.
Compare blocos: registre mudanças, inclusive quando a dispersão não permite decidir qual configuração é melhor.
Explique coalescing (acessos contíguos combinados pelo dispositivo), memória compartilhada e barriers na reduction.

Sem GPU/toolkit, execute os checks CPU e desenhe os índices e passagens para `n=65` e `n=513`.
Conte bytes transferidos e somas necessárias. Identifique essas contagens como análise teórica.
Deixe a tabela de tempos vazia e registre a dependência ausente. Não estime tempos GPU a partir do tempo CPU.
