# Guia local — NOME DO LABORATÓRIO

Leia [o enunciado](index.md) antes de executar os experimentos.

## Ambiente

Informe sistema, arquitetura, compilador/runtime e versões necessárias.
Declare recursos opcionais e limitações de hardware.

## Preparar e executar

Forneça comandos completos a partir deste diretório.
Informe qual arquivo o participante deve editar.
Diferencie uma falha esperada do starter de um erro na preparação.

## Verificar

Forneça o comando dos checks públicos, o status esperado e como interpretar falhas.
Use fixtures independentes. Preserve todos os literais do contrato.

## Registrar

Use [o modelo de relato](report-template.md).
Explique quais saídas, traces ou tabelas devem acompanhar a entrega.

## Licenças

Documentação original: CC BY 4.0. Código original: MIT. Dados originais: CC0 1.0.
Consulte os avisos incluídos no pacote. Identifique materiais de terceiros separadamente.

## Interface Make

Configure `help`, `setup`, `build`, `test`, `run`, `clean` e `verify-preparation`.
Documente o experimento padrão, seletores, falhas esperadas e requisitos do ambiente.
`make` deve mostrar ajuda. Os arquivos gerados devem acompanhar o pacote, sem
dependência no repositório completo. Preserve evidências em `results/` na limpeza.
