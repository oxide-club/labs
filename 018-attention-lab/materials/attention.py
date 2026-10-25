"""SPDX-License-Identifier: MIT — starter incompleto; veja contract.md."""


def scaled_scores(q, k):
    """Devolva Q @ K.T / sqrt(d_k), após validar as entradas."""
    # TODO: validar formas/domínio; transpor K e implementar os produtos.
    raise NotImplementedError('Implemente scaled_scores conforme contract.md')


def softmax(row):
    """Normalize uma linha com subtração do máximo e tratamento de -inf."""
    # TODO: validar; rejeitar linha totalmente mascarada; normalizar com estabilidade.
    raise NotImplementedError('Implemente softmax conforme contract.md')


def attention(q, k, v, *, causal=False):
    """Devolva scores, probabilities e output, preservando as entradas."""
    # TODO: validar Q/K/V; compor scores, causal mask, softmax e produto por V.
    raise NotImplementedError('Implemente attention conforme contract.md')
