# Checks públicos CUDA

O participante implementa `materials/kernels.cu` conforme
[contract.md](../materials/contract.md). O pacote distribui o starter incompleto,
os checks e os experimentos; não distribui uma solução dos kernels.

```sh
make setup MODE=gpu
make build MODE=gpu
make test MODE=gpu
```

`setup` verifica o dispositivo com a sonda de infraestrutura. `build` apenas
compila. O starter retorna `cudaErrorNotSupported`: `test` deve falhar com
`operation not supported` até a implementação. `make run MODE=gpu` repete os
checks antes de medir e recusa produzir medições válidas se eles falharem.

`api.cu` verifica 60 combinações de tamanho e bloco, com:

- entradas distintas das fixtures do CLI;
- vetores vazios, unitários e tamanhos próximos das fronteiras de blocos;
- allocations exatas, sem padding para esconder leitura além da entrada;
- preservação das entradas e soma vazia sem escrita;
- saídas reinicializadas e duas execuções para rejeitar resultados residuais;
- comparação independente da soma vetorial e da redução em inteiros de 64 bits.

`check.py --gpu` executa esses casos e os checks do CLI: limites, tails,
extremos positivos/negativos, rampa acima de 32 bits e rejeições de argumentos.
O runner também verifica sentinelas após a saída vetorial. A suíte para no
primeiro erro; uma falha não significa que todos os casos seguintes foram testados.

Após os checks passarem, complemente a investigação com:

```sh
compute-sanitizer --tool memcheck --leak-check full --error-exitcode 99 materials/build/gpu-api
compute-sanitizer --tool racecheck --error-exitcode 99 materials/build/gpu-api
compute-sanitizer --tool synccheck --error-exitcode 99 materials/build/gpu-api
compute-sanitizer --tool memcheck --leak-check full --error-exitcode 99 materials/build/gpu 4194305 64 29 ramp
```

Esses comandos precisam de acesso à GPU NVIDIA. Erros de dispositivo dentro de
um sandbox devem ser distinguidos de falhas da implementação. Os checks CPU
(`make test MODE=cpu`) verificam somente o suporte auxiliar.

Os checks não provam correção para toda entrada nem cobrem todas as falhas de
allocation/driver. Justifique os invariantes, as barreiras e o tratamento de
erros, além de registrar os resultados observados.
