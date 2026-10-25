# SPDX-License-Identifier: MIT
"""Modelo sequencial explícito, não simulação do comportamento indefinido de C."""
from itertools import combinations

results = set()
for a_positions in combinations(range(6), 3):
    schedule = ["A" if i in a_positions else "B" for i in range(6)]
    shared = 0
    local = {"A": 0, "B": 0}
    step = {"A": 0, "B": 0}
    for thread in schedule:
        if step[thread] == 0:
            local[thread] = shared
        elif step[thread] == 1:
            local[thread] += 1
        else:
            shared = local[thread]
        step[thread] += 1
    results.add(shared)
    print("".join(schedule), shared)
assert results == {1, 2}
print("Modelo: 20 intercalações; resultados 1 e 2. C com data race tem UB.")
