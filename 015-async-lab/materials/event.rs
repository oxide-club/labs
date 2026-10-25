// SPDX-License-Identifier: MIT
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

pub struct Event {
    // TODO: estado persistente e registro do Waker mais recente.
}

#[derive(Clone)]
pub struct Signal {
    // TODO: referência compartilhada segura entre threads.
}

pub fn event() -> (Event, Signal) {
    todo!("crie as duas extremidades do evento")
}

impl Signal {
    pub fn signal(&self) {
        todo!("publique o sinal e notifique sem segurar o lock")
    }
}

impl Future for Event {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        todo!("observe o sinal ou registre o Waker sem perder eventos")
    }
}
