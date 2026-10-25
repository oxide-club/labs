# Materiais — Fuzzing e análise de falhas

**Situação:** materiais aprovados para publicação. Revisão do pacote: `021-c-2026-10-25-v3`.

## Inventário

| Arquivo | Função |
| --- | --- |
| `starter/c/oxf.h` | API de parsing e representação do documento. |
| `starter/c/oxf.c` | Parser didático com dois defeitos intencionais próprios de C. |
| `starter/c/runner.c` | Reprodução determinística fora do motor, com chamadas intercaláveis. |
| `starter/c/fuzz_target.c` | Esqueleto incompleto; o participante constrói seu instrumento. |
| `starter/c/Makefile` | Build C11 com ASan/UBSan; target opcional com libFuzzer. |
| `corpus.json` | Quatro seeds em hexadecimal e contribuição prevista de cada uma. |
| `after-campaign/README.md` | Kit público para consulta após registrar a campanha, com comandos e interpretação. |
| `after-campaign/reproducers.json` | Duas reservas em hexadecimal, hashes e versão do parser. |
| `after-campaign/regression.py` | Suíte completa para a etapa de correção e regressão. |
| `LICENSE.txt` | Licença MIT do código original. |
| `../checks/check.py` | Preparação com expectativas independentes e repetição intercalada; não é regressão completa. |
| `../checks/test_phases.py` | Confere preparação inicial sem revelação automática e integridade do kit público posterior. |
| `../checks/corpus.py` | Materialização do corpus binário em diretório de trabalho. |
| `../checks/campaign.py` | Supervisor com reservas persistentes do orçamento total. |

O [guia local](../README.md) contém os comandos de execução. Nenhum binário ou solução acompanha os materiais.

## Interface auxiliar

`parse(data, size, out)` devolve um `Error`. `out` deve apontar para um `Document` gravável. `data` deve apontar para `size` bytes legíveis; pode ser nulo apenas quando `size == 0`. Uma saída com erro não é utilizável. `Document` contém contagem, presença de checksum, soma em `uint32_t` e até 16 registros na ordem original. Cada registro preserva tipo, comprimento e bytes. Não há propriedade de memória transferida. Os nomes de erro são os do contrato OXF1.

O runner lê uma entrada hexadecimal por linha; uma linha vazia testa `NULL, 0`. Aceita até 4097 bytes para verificar também `TooLarge`. Escreve uma linha por chamada: nome do erro ou `Ok CHECKSUM SOMA CONTAGEM TIPO:HEX ...`. Campos numéricos são decimais; bytes usam hexadecimal minúsculo. Texto vazio aparece como `2:`. Entrada hexadecimal malformada encerra o runner com código 2; isso é erro do transporte auxiliar, não erro OXF1.

O runner usa buffers de comprimento exato para permitir observação por ASan. O check público executa chamadas básicas e intercaladas no mesmo processo. O check completo da etapa posterior também isola casos para que uma falha não esconda as demais. Não comparam padding das estruturas C.

## Oráculo e limites

O check inicial usa resultados literais independentes para casos básicos. O oráculo completo está no [kit público após a campanha](after-campaign/README.md). Ele calcula valores do modelo de registros antes da serialização e inclui violações isoladas e coexistentes. Não usa retornos do parser como expectativa.

O kit contém duas reservas, sintomas esperados, instruções e regressões completas. Não contém a referência corrigida, mutantes ou logs históricos. Por decisão do responsável, não há restrição de acesso: a consulta após a campanha é uma orientação pedagógica. Os comandos iniciais não executam automaticamente o kit nem revelam os diagnósticos dos defeitos.

O participante deve formular hipóteses, implementar o harness e investigar os dois defeitos. O corpus inicial não promete descobri-los no orçamento disponível. Quando usar uma reserva, registre a origem como fornecida pelo clube. Se consultar o apoio antecipadamente, registre isso; uma entrada fornecida não se torna descoberta espontânea por ser executada no motor.

O kit público permanece no pacote após o piloto. Seu manifesto identifica o parser inicial e os bytes de cada reserva. Atualizações do parser exigem nova conferência das reservas e dos resultados esperados.

## Linguagens e ambiente

C11 com Clang/libFuzzer em Linux x86-64 é a variante fornecida. O formato OXF1 e os limites do enunciado permanecem integrais. Rust é alternativa aceita, sem starter ou validação executável neste pacote. Não há dependências baixadas durante build ou execução.

## Origem e licenças

Autoria: colaboradores do Oxide Club, 2026. Código C e Python, Makefile, oráculo e fixtures foram escritos para esta preparação; nenhum código externo foi copiado. Código original: MIT. Dados originais do corpus e vetores: CC0 1.0. Documentação: CC BY 4.0.

Especificação curricular: atividade editorial 32 do caderno `Oxide_Club_Desafios_e_Laboratorios_Rust_Seguranca_Terminologia_Revisada_2026-10-25.md`. Redação: Português Técnico Claro, versão 1.1. Ferramentas externas conservam suas próprias licenças; não são redistribuídas neste pacote.
