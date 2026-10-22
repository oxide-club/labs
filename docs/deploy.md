# Publicar no site

O workflow `Publish website content` solicita o deploy do site quando o conteúdo muda na branch `main`.
Ele acompanha enunciados, materiais, verificações, modelos de relato e licenças.
Mudanças em `templates/` e `docs/` não iniciam o deploy.
Você também pode executar o workflow pela aba Actions.

O workflow chama `deploy.yml` na branch `main` de `oxide-club/oxideclub.dev`.
O site precisa ter o suporte aos laboratórios nessa branch para publicar esse conteúdo.

## Configurar o token

1. Abra a página de [novos tokens fine-grained](https://github.com/settings/personal-access-tokens/new).
2. Defina `oxide-club` como Resource owner.
3. Defina uma data de expiração.
4. Em Repository access, escolha Only select repositories.
5. Selecione apenas `oxideclub.dev`.
6. Em Repository permissions, conceda Actions: Read and write.
7. Crie o token. Se a organização exigir aprovação, aguarde a aprovação.
8. Abra os [secrets de Actions do repositório labs](https://github.com/oxide-club/labs/settings/secrets/actions).
9. Crie um repository secret chamado `WEBSITE_DEPLOY_TOKEN` com o valor do token.

Não coloque o token em arquivos, commits ou mensagens.
Para cadastrar o secret pelo terminal, execute o comando abaixo e informe o token no prompt:

```sh
gh secret set WEBSITE_DEPLOY_TOKEN --repo oxide-club/labs
```

Antes de o token expirar, crie outro com o mesmo acesso e atualize o secret.
Consulte a [documentação de tokens do GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

## Verificar o deploy

1. Execute `Publish website content` na aba Actions de `oxide-club/labs`.
2. Confira o resultado da execução.
3. Abra a aba Actions de `oxide-club/oxideclub.dev`.
4. Confira a validação e o deploy iniciados no site.

O sucesso do workflow de labs confirma o envio da solicitação.
Confira o workflow do site para saber se a publicação terminou.
