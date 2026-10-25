// SPDX-License-Identifier: MIT
#[cfg(feature = "model")]
pub use loom::{sync::{Arc, atomic::{AtomicBool, AtomicUsize, Ordering}}, thread};
#[cfg(not(feature = "model"))]
pub use std::{sync::{Arc, atomic::{AtomicBool, AtomicUsize, Ordering}}, thread};
#[derive(Clone, Copy, Debug)]
pub enum Variant { Weak, Publish, Strong }
pub struct State { pub data: AtomicUsize, pub ready: AtomicBool }
impl State {
    pub fn new() -> Self { Self { data: AtomicUsize::new(0), ready: AtomicBool::new(false) } }
    pub fn publish(&self, _variant: Variant) { todo!("implemente os dois stores na ordem do contrato") }
    pub fn try_read(&self, _variant: Variant) -> Option<usize> { todo!("implemente uma tentativa de leitura") }
}
