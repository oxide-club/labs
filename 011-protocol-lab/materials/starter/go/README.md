# Starter Go de protocolos

Use Go 1.20+ e sua biblioteca padrão. Não há módulos externos nem gerador de
protocolo. Execute a partir da raiz do laboratório:

```sh
cd materials/starter/go
go test -run '^TestFixtures$' .
go test -run '^$' .
go test -timeout 30s .
go test -race -timeout 60s .
```

Os dois primeiros comandos verificam fixtures e compilação. Os demais devem
rejeitar o starter por TODO; depois da implementação, devem passar. `-race` exige
suporte do ambiente e compilador C auxiliar. Não é obrigatório para usar outra
variante. Os vetores vêm de `../../vectors.json`, sem cópia por linguagem.

Para executar todos os grupos mesmo quando um TODO causa panic, use
`python3 checks/go.py` na raiz do laboratório. O starter passa apenas no grupo
de fixtures: `1/4 grupos Go passaram`, status 1. Use `--compile-only`,
`--fixture-only` ou `--race` para selecionar a verificação. Um erro de build ou
timeout reprova a preparação; não conta como rejeição esperada do starter.

## API adaptada

`Message{Flags int, Payload []byte}` só armazena campos. `Encode` retorna bytes
novos ou `ErrArgument` para flags fora de 0/1 ou payload maior que 4096, nessa
ordem. Um slice nil representa payload vazio; Go não tem a distinção Python
entre `None` e `bytes` nessa assinatura. Tipos incompatíveis são erros de build.

`NewDecoder` cria uma instância ativa. `Feed` recebe até 65536 bytes; nil ou slice
vazio não significa EOF. Um chunk grande retorna `ErrArgument` sem alterar o
estado. Retorno normal contém as mensagens em ordem e erro nil. Uma falha de
protocolo retorna slice nil e `*ProtocolError{Code, Completed}`, com os mesmos
códigos e a mesma precedência do enunciado. `Completed` contém somente mensagens
concluídas nesta chamada. Não retorne essas mensagens também no primeiro valor.

`Finish` retorna nil no EOF válido ou `*ProtocolError` com código de truncamento
e Completed vazio. Sucesso ou falha terminal impedem novas operações: `Feed` e
`Finish` retornam `ErrTerminal`, antes de validar o argumento. Não há reset.

Copie os bytes para que alterações no chunk, chamadas futuras ou outra instância
não alterem mensagens retornadas. Não retenha chunks nem mensagens entregues.
Entre chamadas, retenha no máximo 4104 bytes de dados do protocolo; após término,
zero. Os checks de valores não comprovam esse limite: revise retenção de slices,
capacidade dos buffers e custo das cópias. Não acumule chunks completos.

Implemente framing e parsing; usar `encoding/json` nos testes para ler fixtures
não autoriza substituir o parser binário por uma biblioteca pronta.
O starter Python continua no caminho histórico `materials/protocol.py`.
