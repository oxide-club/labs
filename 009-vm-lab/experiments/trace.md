# Experimento — PC, opcode e stack

Antes de executar, preveja os PCs visitados em `materials/branch.txt`. Em seguida, use:

```sh
python3 experiments/trace.py materials/branch.txt
python3 experiments/trace.py materials/loop.txt
```

O script imprime o resultado JSON, incluindo o trace anterior a cada instrução.
Compare o trace completo com `materials/cases.json`. No laço, marque as visitas ao PC 3: os topos devem ser 2, 1 e 0.
Explique por que JZ remove o teste em todas as visitas e por que o PC 9 só aparece após o zero.
Substitua, numa cópia local, `JMP 2` por `JMP 8`. Preveja a última stack e o erro antes de executar com budget 25.
Registre 25 passos concluídos e explique o papel do budget. Não confunda este limite com prova de término do programa.
