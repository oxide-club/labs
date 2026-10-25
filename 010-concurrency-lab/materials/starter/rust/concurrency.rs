// SPDX-License-Identifier: MIT
#[derive(Clone, Copy)]
pub enum CounterMode { Mutex, Atomic }

#[derive(Debug, PartialEq, Eq)]
#[allow(dead_code)] // Erros que o participante deve produzir nos caminhos de falha.
pub enum RunError { Invalid, Spawn, Panicked }

pub fn counter_run(_mode: CounterMode, _threads: u32, _iterations: u32) -> Result<u64, RunError> {
    // TODO: um Mutex<u64> ou AtomicU64 conforme modo; incrementos reais por thread.
    // Use Builder::spawn para tratar falha de criação e reúna threads já criadas.
    todo!("implemente contador e join")
}

#[derive(Debug, PartialEq, Eq)]
#[allow(dead_code)] // Erros que o participante deve produzir nos caminhos de falha.
pub enum QueueError { Invalid, Closed, Poisoned }

pub struct BoundedQueue {
    // TODO: Mutex protegendo buffer circular, índices, count e closed;
    // duas Condvar para predicados não vazia/não cheia. Capacidade fixa 1..64.
}

impl BoundedQueue {
    pub fn new(_capacity: usize) -> Result<Self, QueueError> {
        todo!("crie fila aberta e vazia")
    }
    pub fn push(&self, _id: u64) -> Result<(), QueueError> {
        todo!("espere por espaço ou fechamento, reavaliando o predicado")
    }
    pub fn pop(&self) -> Result<Option<u64>, QueueError> {
        todo!("espere por item ou fechamento; drene antes de retornar None")
    }
    pub fn close(&self) -> Result<(), QueueError> {
        todo!("feche de modo idempotente e notifique todos os esperadores")
    }
}

pub fn ordered() -> Result<(), RunError> {
    // TODO: duas threads, dois mutexes, mesma ordem global; reúna ambas.
    // Não mantenha a barrier do cenário C defeituoso entre as aquisições.
    todo!("implemente aquisição ordenada e término")
}
