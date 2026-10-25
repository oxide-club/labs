# Computação Paralela em GPU

Leia o [enunciado](index.md) e o [contrato](materials/contract.md).
A partir deste diretório, prepare e verifique o suporte sem GPU:

```sh
make -C materials cpu
python3 checks/check.py
```

Com CUDA Toolkit e GPU compatível, compile e teste o trabalho do participante:

```sh
make -C materials gpu
materials/build/probe
python3 checks/check.py --gpu
```

Edite `materials/kernels.cu`. O starter retorna `cudaErrorNotSupported`; os checks GPU devem falhar até a implementação.
Compilação CUDA, probe, checks GPU e medição foram executados em 25/10/2026 na RTX 4060, com nvcc 13.4 e driver 615.78.08. Uma implementação privada passou; o starter mantém os TODOs. Veja o registro de preparação.
Use o [roteiro](experiments/README.md) somente depois dos checks GPU.
Registre ambiente, evidências e limitações no [modelo de relato](report-template.md).
Documentação original: CC BY 4.0. Código original: MIT. Dados de `datasets.csv`: CC0 1.0.
O pacote é independente; não requer arquivos fora deste diretório.

`materials/build/probe` verifica dispositivo, runtime, allocation e cópias, sem executar kernels próprios.
Seu sucesso verifica apenas essa infraestrutura; não valida o exercício nem produz medição.
