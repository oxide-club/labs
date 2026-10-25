// SPDX-License-Identifier: MIT
pub trait Op { fn apply(&self, x: u64) -> u64; }
pub struct Add { pub delta: u64 }
pub struct Mul { pub factor: u64 }
pub enum Operation { Add(Add), Mul(Mul) }
impl Op for Add {
    fn apply(&self, _x: u64) -> u64 { todo!("implemente Add com wrapping") }
}
impl Op for Mul {
    fn apply(&self, _x: u64) -> u64 { todo!("implemente Mul com wrapping") }
}
pub fn generic<T: Op>(_input: &[u64], _op: &T) -> u64 {
    todo!("implemente o processador genérico")
}
pub fn dynamic(_input: &[u64], _op: &dyn Op) -> u64 {
    todo!("implemente o processador dinâmico")
}
pub fn enumerated(_input: &[u64], _op: &Operation) -> u64 {
    todo!("implemente o processador por enum")
}
