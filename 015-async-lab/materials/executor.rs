// SPDX-License-Identifier: MIT
use std::future::Future;

pub type TaskId = usize;

#[derive(Debug, PartialEq, Eq)]
pub enum Step {
    Polled { id: TaskId, ready: bool },
    Idle,
    Complete,
}

pub struct Executor {
    // TODO: estado local das futures e estado compartilhado das notificações.
}

impl Executor {
    pub fn new() -> Self {
        todo!("inicialize o executor vazio")
    }

    pub fn spawn<F: Future<Output = ()> + 'static>(&mut self, _future: F) -> TaskId {
        todo!("guarde a future fixada e agende o primeiro poll")
    }

    pub fn step(&mut self) -> Step {
        todo!("consulte no máximo uma tarefa pronta")
    }

    pub fn run(&mut self) {
        todo!("execute até concluir, bloqueando quando necessário")
    }

    pub fn active(&self) -> usize {
        todo!("conte tarefas ainda não concluídas")
    }
}
