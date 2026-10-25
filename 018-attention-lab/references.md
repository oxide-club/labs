# Referências e leitura orientada

As leituras aprofundam o mecanismo depois do núcleo. O contrato local define
as entradas e erros exigidos no exercício.

- [Vaswani et al., Attention Is All You Need](https://arxiv.org/abs/1706.03762):
  apresenta scaled dot-product attention. Localize a expressão com `sqrt(d_k)`
  e relacione cada dimensão aos intermediários locais. O artigo trata uma
  arquitetura completa; aqui Q/K/V já são fornecidos. Pergunta: qual dimensão
  determina o divisor e qual determina a largura da saída?
- [Dao et al., FlashAttention](https://arxiv.org/abs/2205.14135): descreve
  attention exata com tiling para reduzir movimentação de dados. Compare a
  materialização N × N do exercício com a organização por blocos. Pergunta:
  por que evitar guardar todos os scores pode reduzir memória sem definir
  uma operação matemática aproximada?

## Código real: llama2.c

[run.c, revisão 2fbf7059aab6f7e44047da1ff5c0ba53057a248e](https://github.com/karpathy/llama2.c/blob/2fbf7059aab6f7e44047da1ff5c0ba53057a248e/run.c)
implementa inferência de um transformer em C. Observe `softmax`, a divisão
por `sqrtf(head_size)` em `forward`, a soma ponderada de valores e os buffers
`key_cache`, `value_cache` e `att` de `RunState`.

O código usa `float`, projeções, múltiplas cabeças e geração token a token.
O exercício usa binary64, uma cabeça e a sequência inteira; por isso materializa
scores e probabilidades separadamente. Compare o limite `t <= pos` com a
causal mask: as posições futuras nem entram na soma desse forward pass.
Pergunta de leitura: quais buffers podem ser reutilizados a cada token e quais
precisam preservar dados para a geração seguinte?

## Registro de acesso

Consulta em 25/10/2026. As páginas dos dois artigos responderam. O arquivo
[run.c em master](https://github.com/karpathy/llama2.c/blob/master/run.c) foi
lido e os mecanismos acima foram conferidos. O
[histórico de run.c](https://github.com/karpathy/llama2.c/commits/master/run.c)
e o [commit identificado](https://github.com/karpathy/llama2.c/commit/2fbf7059aab6f7e44047da1ff5c0ba53057a248e)
responderam e permitiram registrar o SHA. O acesso ao conteúdo no endereço
fixado e ao raw fixado retornou `Cache miss` na ferramenta de navegação.
O conteúdo do SHA fixado não foi conferido byte a byte nesta preparação;
a evidência de leitura do mecanismo é a página master. Não foi copiado código de terceiros.
