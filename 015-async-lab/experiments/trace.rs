// SPDX-License-Identifier: MIT
#![allow(dead_code)]
#[path = "../materials/event.rs"]
mod event;
#[path = "../materials/executor.rs"]
mod executor;

use executor::{Executor, Step};
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

struct Logged<F: ?Sized> {
    name: &'static str,
    future: Pin<Box<F>>,
}
impl<F: Future<Output = ()> + ?Sized> Future for Logged<F> {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        println!("poll {}", self.name);
        let result = self.future.as_mut().poll(cx);
        println!("result {} {:?}", self.name, result);
        result
    }
}

struct YieldOnce(bool);
impl Future for YieldOnce {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if self.0 {
            return Poll::Ready(());
        }
        self.0 = true;
        println!("wake yield (duas notificações durante poll)");
        cx.waker().wake_by_ref();
        cx.waker().wake_by_ref();
        Poll::Pending
    }
}

fn main() {
    println!("OBSERVAÇÃO: trace desta execução, não uma previsão");
    let mut executor = Executor::new();
    let (event, signal) = event::event();
    for (name, future) in [
        (
            "event",
            Box::pin(event) as Pin<Box<dyn Future<Output = ()>>>,
        ),
        (
            "yield",
            Box::pin(YieldOnce(false)) as Pin<Box<dyn Future<Output = ()>>>,
        ),
    ] {
        let id = executor.spawn(Logged {
            name,
            future,
        });
        println!("spawn {name} id={id}");
    }
    for turn in 0..4 {
        println!("step {turn}: {:?}", executor.step());
    }
    println!("signal event (duas chamadas)");
    signal.signal();
    signal.signal();
    // Limite didático; o runner também protege contra bloqueio dentro de step.
    for turn in 4..8 {
        let step = executor.step();
        println!("step {turn}: {step:?}");
        if step == Step::Complete {
            assert_eq!(executor.active(), 0);
            return;
        }
    }
    panic!("trace não concluiu no número de passos previsto pelo contrato");
}
