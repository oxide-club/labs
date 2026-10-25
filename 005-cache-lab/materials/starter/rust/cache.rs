// SPDX-License-Identifier: MIT
// Starter: não contém a política de acesso nem a leitura do trace.
#[derive(Clone, Copy, Default)]
pub struct Line {
    pub valid: bool,
    pub tag: u64,
}

#[derive(Default)]
pub struct Cache {
    pub lines: [Line; 4],
    pub hits: u64,
    pub misses: u64,
    pub evictions: u64,
}

impl Cache {
    pub fn access(&mut self, _address: u64) {
        todo!("calcule índice/tag e atualize estado e contadores")
    }
}

fn main() {
    // TODO: leia stdin; cada linha válida é L 0xENDERECO.
    // Chame access para cada endereço. Ao fim, imprima os três contadores.
    eprintln!("Implemente a leitura dos traces e o modelo da cache.");
    std::process::exit(1);
}
