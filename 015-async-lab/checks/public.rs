// SPDX-License-Identifier: MIT
#[path = "../materials/event.rs"]
mod event;
#[path = "../materials/executor.rs"]
mod executor;

use executor::{Executor, Step};
use std::cell::{Cell, RefCell};
use std::future::Future;
use std::pin::Pin;
use std::rc::Rc;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{mpsc, Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::time::Duration;

// Future de teste independente de materials/event.rs.
#[derive(Default)]
struct Control {
    ready: bool,
    polls: usize,
    drops: usize,
    waker: Option<Waker>,
}

struct Controlled(Arc<Mutex<Control>>);

impl Future for Controlled {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let mut state = self.0.lock().unwrap();
        state.polls += 1;
        state.waker = Some(cx.waker().clone());
        if state.ready {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

impl Drop for Controlled {
    fn drop(&mut self) {
        self.0.lock().unwrap().drops += 1;
    }
}

fn controlled() -> (Controlled, Arc<Mutex<Control>>) {
    let state = Arc::new(Mutex::new(Control::default()));
    (Controlled(state.clone()), state)
}

fn notify(state: &Arc<Mutex<Control>>, ready: bool) {
    let waker = {
        let mut state = state.lock().unwrap();
        state.ready = ready;
        state.waker.clone().expect("primeiro poll registra Waker")
    };
    waker.wake();
}

#[derive(Default)]
struct CountWake(AtomicUsize);
impl Wake for CountWake {
    fn wake(self: Arc<Self>) {
        self.0.fetch_add(1, Ordering::SeqCst);
    }
}

#[test]
fn fixture_controlled_future() {
    let (future, state) = controlled();
    let mut future = Box::pin(future);
    let count = Arc::new(CountWake::default());
    let waker = Waker::from(count.clone());
    let mut cx = Context::from_waker(&waker);
    assert_eq!(future.as_mut().poll(&mut cx), Poll::Pending);
    notify(&state, true);
    assert_eq!(count.0.load(Ordering::SeqCst), 1);
    assert_eq!(future.as_mut().poll(&mut cx), Poll::Ready(()));
    drop(future);
    assert_eq!(state.lock().unwrap().polls, 2);
    assert_eq!(state.lock().unwrap().drops, 1);
}

#[test]
fn empty_reuse_and_local_future() {
    let mut ex = Executor::new();
    assert_eq!(ex.active(), 0);
    assert_eq!(ex.step(), Step::Complete);
    ex.run();
    let value = Rc::new(Cell::new(0));
    let local = value.clone();
    let id = ex.spawn(async move { local.set(7) });
    assert_eq!(id, 0);
    assert_eq!(value.get(), 0, "spawn não executa poll");
    assert_eq!(ex.active(), 1);
    ex.run();
    assert_eq!(value.get(), 7);
    assert_eq!(ex.active(), 0);
    assert_eq!(ex.spawn(async {}), 1);
    ex.run();
    assert_eq!(ex.step(), Step::Complete);
}

#[test]
fn pending_duplicates_and_late_wake() {
    let mut ex = Executor::new();
    let (future, state) = controlled();
    let id = ex.spawn(future);
    assert_eq!(ex.step(), Step::Polled { id, ready: false });
    for _ in 0..32 {
        assert_eq!(ex.step(), Step::Idle);
    }
    assert_eq!(state.lock().unwrap().polls, 1);
    for _ in 0..100 {
        notify(&state, false);
    }
    assert_eq!(ex.step(), Step::Polled { id, ready: false });
    assert_eq!(ex.step(), Step::Idle, "wakeups duplicados se fundem");
    notify(&state, true);
    assert_eq!(ex.step(), Step::Polled { id, ready: true });
    assert_eq!(state.lock().unwrap().drops, 1);
    for _ in 0..100 {
        notify(&state, true);
    }
    assert_eq!(ex.step(), Step::Complete);
    ex.run(); // Waker ainda retido não impede término.
    assert_eq!(state.lock().unwrap().polls, 3);
    drop(ex);
    notify(&state, true); // Waker sobrevive ao executor.
}

struct Yielding {
    label: u8,
    left: u8,
    log: Rc<RefCell<Vec<u8>>>,
    owner: thread::ThreadId,
}
impl Future for Yielding {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        assert_eq!(thread::current().id(), self.owner);
        self.log.borrow_mut().push(self.label);
        // Até o poll final notifica: Ready deve invalidar o reagendamento.
        cx.waker().wake_by_ref();
        cx.waker().clone().wake();
        if self.left == 0 {
            Poll::Ready(())
        } else {
            self.left -= 1;
            Poll::Pending
        }
    }
}

#[test]
fn wake_during_poll_fifo_and_ready() {
    let mut ex = Executor::new();
    let log = Rc::new(RefCell::new(Vec::new()));
    for label in [0, 1] {
        ex.spawn(Yielding {
            label,
            left: 2,
            log: log.clone(),
            owner: thread::current().id(),
        });
    }
    ex.run();
    assert_eq!(*log.borrow(), [0, 1, 0, 1, 0, 1]);
    assert_eq!(ex.active(), 0);
    assert_eq!(ex.step(), Step::Complete);
}

#[test]
fn selective_wake_and_drop_pending() {
    let mut ex = Executor::new();
    let (a, a_state) = controlled();
    let (b, b_state) = controlled();
    let a_id = ex.spawn(a);
    let b_id = ex.spawn(b);
    assert_eq!(
        ex.step(),
        Step::Polled {
            id: a_id,
            ready: false
        }
    );
    assert_eq!(
        ex.step(),
        Step::Polled {
            id: b_id,
            ready: false
        }
    );
    notify(&b_state, true);
    assert_eq!(
        ex.step(),
        Step::Polled {
            id: b_id,
            ready: true
        }
    );
    assert_eq!(ex.active(), 1);
    assert_eq!(a_state.lock().unwrap().polls, 1);
    assert_eq!(ex.step(), Step::Idle);
    drop(ex);
    assert_eq!(a_state.lock().unwrap().drops, 1);
    notify(&a_state, true);
}

struct ThreadEvent {
    state: Arc<Mutex<Control>>,
    first: Option<mpsc::Sender<()>>,
    owner: thread::ThreadId,
}
impl Future for ThreadEvent {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        assert_eq!(thread::current().id(), self.owner);
        let ready = {
            let mut state = self.state.lock().unwrap();
            state.polls += 1;
            state.waker = Some(cx.waker().clone());
            state.ready
        };
        if let Some(tx) = self.first.take() {
            tx.send(()).unwrap();
        }
        if ready {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

#[test]
fn thread_notification_and_run_waits() {
    let mut ex = Executor::new();
    let state = Arc::new(Mutex::new(Control::default()));
    let worker_state = state.clone();
    let (tx, rx) = mpsc::channel();
    ex.spawn(ThreadEvent {
        state: state.clone(),
        first: Some(tx),
        owner: thread::current().id(),
    });
    let worker = thread::spawn(move || {
        rx.recv_timeout(Duration::from_secs(2)).unwrap();
        // Somente janela de observação; ordem causal vem do canal e do lock.
        thread::sleep(Duration::from_millis(50));
        let before = worker_state.lock().unwrap().polls;
        notify(&worker_state, true);
        before
    });
    ex.run();
    let active_on_return = ex.active();
    let before = worker.join().unwrap();
    assert_eq!(active_on_return, 0, "run não retorna em Idle");
    assert_eq!(before, 1, "nenhum poll novo antes do sinal");
    assert_eq!(state.lock().unwrap().polls, 2);
    assert!(state.lock().unwrap().ready);
}

#[test]
fn event_before_poll_and_repeated_signal() {
    fn send_sync<T: Send + Sync>() {}
    send_sync::<event::Signal>();
    let (future, signal) = event::event();
    let clone = signal.clone();
    signal.signal();
    clone.signal();
    let mut future = Box::pin(future);
    let waker = Waker::from(Arc::new(CountWake::default()));
    assert_eq!(
        future.as_mut().poll(&mut Context::from_waker(&waker)),
        Poll::Ready(())
    );
    drop(future);
    signal.signal();
}

#[test]
fn event_latest_waker_and_thread_signal() {
    let (future, signal) = event::event();
    let mut future = Box::pin(future);
    let old = Arc::new(CountWake::default());
    let new = Arc::new(CountWake::default());
    for counter in [&old, &new] {
        let waker = Waker::from(counter.clone());
        assert_eq!(
            future.as_mut().poll(&mut Context::from_waker(&waker)),
            Poll::Pending
        );
    }
    thread::spawn(move || {
        signal.signal();
        signal.signal();
    })
    .join()
    .unwrap();
    assert_eq!(old.0.load(Ordering::SeqCst), 0);
    assert_eq!(new.0.load(Ordering::SeqCst), 1);
    let waker = Waker::from(new);
    assert_eq!(
        future.as_mut().poll(&mut Context::from_waker(&waker)),
        Poll::Ready(())
    );
}

// Linux mede somente a thread que executa run; a thread produtora não entra na conta.
#[cfg(target_os = "linux")]
fn wait_counters() -> (u64, u64) {
    let stat = std::fs::read_to_string("/proc/thread-self/stat").expect("procfs stat");
    let fields: Vec<_> = stat.rsplit_once(')').unwrap().1.split_whitespace().collect();
    let cpu = fields[11].parse::<u64>().unwrap() + fields[12].parse::<u64>().unwrap();
    let status = std::fs::read_to_string("/proc/thread-self/status").expect("procfs status");
    let switches = status.lines().find_map(|line| line.strip_prefix("voluntary_ctxt_switches:"))
        .unwrap().trim().parse().unwrap();
    (cpu, switches)
}

#[test]
#[cfg(target_os = "linux")]
fn run_waits_without_spin_or_sleep_polling() {
    let ticks = std::process::Command::new("getconf").arg("CLK_TCK").output().unwrap();
    assert!(ticks.status.success());
    let hz: u64 = std::str::from_utf8(&ticks.stdout).unwrap().trim().parse().unwrap();
    let mut ex = Executor::new();
    let state = Arc::new(Mutex::new(Control::default()));
    let (tx, rx) = mpsc::channel();
    ex.spawn(ThreadEvent { state: state.clone(), first: Some(tx), owner: thread::current().id() });
    let worker = thread::spawn(move || {
        rx.recv_timeout(Duration::from_secs(2)).unwrap();
        thread::sleep(Duration::from_millis(300));
        notify(&state, true);
    });
    let before = wait_counters();
    ex.run();
    let after = wait_counters();
    worker.join().unwrap();
    let cpu_ms = (after.0-before.0)*1000/hz;
    let switches = after.1-before.1;
    assert!(cpu_ms < 100, "espera consumiu {cpu_ms} ms de CPU em janela de 300 ms");
    assert!(switches < 80, "{switches} esperas voluntárias: possível sleep-polling");
    assert_eq!(ex.active(), 0);
}

struct ReentrantWake(event::Signal);
impl Wake for ReentrantWake {
    fn wake(self: Arc<Self>) { self.0.signal(); }
}
#[test]
fn event_reentrant_wake_releases_lock() {
    let (future, signal) = event::event();
    let mut future = Box::pin(future);
    let waker = Waker::from(Arc::new(ReentrantWake(signal.clone())));
    assert_eq!(future.as_mut().poll(&mut Context::from_waker(&waker)), Poll::Pending);
    signal.signal();
    assert_eq!(future.as_mut().poll(&mut Context::from_waker(&waker)), Poll::Ready(()));
}
