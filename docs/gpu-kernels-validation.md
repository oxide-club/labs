# Validação dos checks CUDA — 25/10/2026

O pacote público contém o starter incompleto, contrato, checks e experimentos.
A implementação de referência foi retirada da entrega por solicitação do
responsável e preservada somente como controle privado de validação.
Fixtures, limites e oráculos não foram relaxados. Os resultados positivos abaixo
se referem ao controle privado, não ao starter distribuído.

## Verificação real

Ambiente: RTX 4060, driver NVIDIA 615.78.08, nvcc 13.4.92, runtime/driver CUDA
13040, Linux 7.2.8-9-omarchy. Os testes foram executados fora do sandbox, com
acesso aos dispositivos NVIDIA.

- Antes da implementação, os novos checks diretos da API falharam com
  `operation not supported` contra o starter.
- Com o controle privado, `make test MODE=gpu` passou: 60 casos da API com
  saídas reinicializadas, entradas preservadas e allocations exatas, além dos
  casos públicos do CLI, extremos inteiros, rampa, limites, tails e rejeições.
- Memcheck nos 60 casos: zero erros e zero bytes vazados.
- Racecheck nos 60 casos: zero hazards, erros ou warnings.
- Synccheck nos 60 casos: zero erros.
- Memcheck adicional com n=4194305, bloco 64 e modo ramp: zero erros e vazamentos.
- `make run MODE=gpu` passou, repetiu os checks e produziu 120 medições:
  três tamanhos × quatro blocos × dez repetições.
- A suíte Python passou com 46 testes. Gerador Make, relatórios e validação
  estrutural passaram; os 18 laboratórios não apresentaram erros estruturais.

[Logs e hashes dos fontes](evidence/2026-10-25-gpu-kernels/) e
[medições brutas](evidence/2026-10-25-gpu-kernels/measurements.csv).
Tempos de uma sessão nessa placa não estabelecem uma conclusão geral de
performance. As medições foram concluídas antes do Memcheck adicional; tempos
produzidos sob sanitização não fazem parte do CSV de medições.

## Revisão e limites

A revisão independente não encontrou problemas materiais nos kernels.
Não houve injeção de falhas de allocation ou deallocation CUDA: essas condições não foram exercitadas dinamicamente. O runner
verifica liberações no caminho de sucesso; o destruidor do harness adicional da
API faz limpeza de fallback sem reportar erros de cudaFree. Os diagnósticos
acima não substituem cobertura de todas as possíveis falhas do driver.
A solução e as notas detalhadas do algoritmo não integram o pacote público.
O starter deve compilar, mas deve ser rejeitado pelos checks GPU.

## Entrega com starter restaurado

O pacote foi exportado pelo empacotador real do website, fora do repositório,
com `checks/api.cu`, `checks/README.md`, Makefiles e helpers locais. Na RTX 4060,
`make setup MODE=gpu` e `make build MODE=gpu` retornaram 0. `make test MODE=gpu`
e `make run MODE=gpu` retornaram 2 por `operation not supported`; o stdout da
medição ficou vazio. Veja [os status e logs](evidence/2026-10-25-gpu-starter/results.json).
A suíte Python passou com 46 testes, e a validação estrutural dos 18 laboratórios
não encontrou erros.

Os hashes em `2026-10-25-gpu-kernels/inputs-sha256.json` identificam o controle
privado usado na validação positiva. O hash de kernels.cu desse controle não
deve corresponder ao starter público restaurado. O código do controle não é
incluído nas evidências nem no pacote.

O branch de entrega foi criado a partir de 2144650, anterior ao commit local
49b4a37 que continha a solução. Esse commit não é ancestral da entrega.
O histórico anterior foi preservado localmente, separado do branch de entrega;
nenhum branch foi enviado ao remoto por esta operação.
