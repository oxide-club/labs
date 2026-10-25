# Referências orientadas

Estas leituras ajudam a interpretar os resultados. O contrato do laboratório
continua sendo a referência para sua implementação.

## Regras de C e representação

- [WG14 N1570, rascunho público de C11](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf),
  seções 6.5.7 e 7.20.1.1. Consulte limites e tipos dos deslocamentos e os inteiros
  de largura exata. Pergunta: por que deslocar pela largura do operando não é uma
  forma válida de tratar a rotação por zero?
- [CS:APP, terceira edição](https://csapp.cs.cmu.edu/3e/), capítulo 2,
  *Representing and Manipulating Information*. Apoio conceitual sobre inteiros,
  bits e bytes; o capítulo não define o header deste laboratório.

## Código real: Protobuf

[Protocol Buffers, coded_stream.cc no commit 2d4414f384dc499af113b5991ce3eaa9df6dd931
(v29.0)](https://github.com/protocolbuffers/protobuf/blob/2d4414f384dc499af113b5991ce3eaa9df6dd931/src/google/protobuf/io/coded_stream.cc).
Procure `ReadLittleEndian32Fallback` e `ReadRaw`. Observe como a leitura de um
inteiro fixo considera os bytes disponíveis antes de avançar o buffer. Compare
isso com a pré-condição de quatro bytes válidos da nossa API. Protobuf também
implementa varints, um formato diferente do header fixo deste exercício.
Pergunta: em que camada um leitor com tamanho conhecido deve rejeitar uma entrada
truncada? Não copie o mecanismo como solução de `header_pack`.

## Código real: Linux

[Linux, if_ether.h no commit adc218676eef25575469234709c2d87185ca223a
(v6.12)](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/include/uapi/linux/if_ether.h).
Procure `ETH_ALEN`, `ETH_HLEN`, `struct ethhdr` e `__be16 h_proto`. Observe como a
interface identifica tamanho e ordem de bytes de campos do formato Ethernet.
O campo de protocolo é big-endian; o exercício do clube exige little-endian.
Esse header usa recursos próprios do Linux, incluindo `packed`; isso não torna
o layout de uma `struct` C11 comum um formato externo portável.
Pergunta: o que precisa ser definido além do nome e tipo C de um campo para que
outra máquina interprete os mesmos bytes?

## Verificação e limites do acesso

Em 25/10/2026, `git ls-remote` confirmou os commits associados às tags v29.0 e
v6.12. O arquivo Protobuf foi baixado pelo URL raw do commit e as funções acima
foram inspecionadas. O arquivo Linux foi inspecionado via GitHub na tag v6.12;
o acesso web direto ao URL do commit retornou cache miss, mas a tag foi resolvida
para o commit citado. O PDF N1570 foi acessado. O site CS:APP é uma referência de
apoio curricular; o conteúdo do livro não foi verificado integralmente nesta
preparação. Nenhum desses fontes externos está incluído no pacote.
