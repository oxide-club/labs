# Starter Rust de cache

Use Rust com edição 2021 e Python 3. Não há crates, Cargo ou rede obrigatórios.
Na raiz do laboratório:

```sh
rustc --edition=2021 -D warnings materials/starter/rust/cache.rs -o /tmp/oxide-cache-rust
python3 checks/check.py /tmp/oxide-cache-rust
```

O build deve passar; o check deve rejeitar o starter até você implementar leitura,
transições e saída. Os seis casos são os mesmos usados para C. Execute também os
dois traces em `materials/inputs/` e os experimentos do enunciado.
Não use uma biblioteca de simulação de cache. `u64` preserva endereços; contadores
não devem transbordar silenciosamente. `valid` é independente do valor da tag.

O arquivo C continua em `../cache.c` para preservar links publicados. Novos
starters têm diretórios de linguagem; não é necessário mover a versão histórica.
