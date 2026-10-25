# Referências de Cache e Localidade

## Leitura principal

[CS:APP, capítulo 6 — The Memory Hierarchy](https://csapp.cs.cmu.edu/3e/).
Estude blocos, mapeamento direto e localidade espacial e temporal.
O livro oferece o fundamento; o contrato deste laboratório define suas quatro linhas de 16 bytes.

## Documentação técnica

[Manual do Cachegrind, seções 5.2.11 e 5.8](https://valgrind.org/docs/manual/cg-manual.html).
Consulta em 25/10/2026: a documentação distingue contagem de instruções, simulação de caches e medidas de hardware.
Use essa distinção para limitar suas conclusões.

## Código real — após concluir o núcleo

[Valgrind, cachegrind/cg_sim.c](https://github.com/tklengyel/valgrind/blob/88813f16d17607abf985957d08267417095e6e87/cachegrind/cg_sim.c).

- Linguagem: C. Tipo: código de produção, em um espelho do projeto.
- Mecanismo: simulação de referências a caches, incluindo conjuntos e associatividade.
- Observe a representação das tags e as alterações no estado após hit e miss.
- Compare a manutenção da recência com a linha única por índice do laboratório.
- Diferença: o Cachegrind representa uma hierarquia mais rica e não implementa o contrato de saída deste exercício.
- Pergunta: qual estado adicional é necessário quando dois blocos podem ocupar o mesmo conjunto?

Arquivo e mecanismo consultados em 25/10/2026 pela branch master.
`git ls-remote` confirmou a revisão `88813f16d17607abf985957d08267417095e6e87`; o link foi fixado nessa revisão.
A ferramenta web não recuperou o raw URL por SHA; a leitura do conteúdo ocorreu na página da branch.
Nenhum código do Valgrind foi copiado para o laboratório.

## Aprofundamento opcional

[Zhirkov, capítulo 16 — Performance](https://link.springer.com/book/10.1007/978-1-4842-2403-8).
Compare os limites do simulador com prefetching e otimizações de uma máquina real.
Essa leitura não é necessária para concluir o núcleo.
