# Materiais de Cache e Localidade

- `starter/cache.c`: esqueleto C compilável, intencionalmente incompleto.
- `inputs/trace-a.txt`: oito leituras para previsão manual.
- `inputs/trace-b.txt`: dezesseis leituras para verificar substituições.
- `../checks/check.py`: verifica contadores do seu executável em casos conhecidos.
- `../report-template.md`: estrutura sugerida para o relato.

Na raiz extraída do laboratório:

```sh
cc -std=c11 -Wall -Wextra -Wpedantic -O2 materials/starter/cache.c -o cache
python3 checks/check.py ./cache
```

O esqueleto compila, mas falha nas verificações até ser implementado.
Python 3 é usado apenas pelo verificador. O gerador de percursos de matriz faz
parte da entrega do participante e pode ser escrito em uma linguagem à escolha.
