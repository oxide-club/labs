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
