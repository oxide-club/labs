// SPDX-License-Identifier: MIT
#[path = "../../materials/starter/rust/concurrency.rs"]
mod concurrency;
use concurrency::{counter_run, ordered, BoundedQueue, CounterMode, QueueError, RunError};
use std::sync::{mpsc, Arc};
use std::thread;
use std::time::Duration;

fn invalid() {
    for (t,n) in [(0,1),(33,1),(1,1_000_001)] {
        assert_eq!(counter_run(CounterMode::Mutex,t,n),Err(RunError::Invalid));
    }
    for capacity in [0,65,usize::MAX] {
        assert!(matches!(BoundedQueue::new(capacity), Err(QueueError::Invalid)));
    }
}
fn counter(mode: CounterMode) {
    for t in [1,2,7,32] { for n in [0,1,193,10000] {
        assert_eq!(counter_run(mode,t,n), Ok(u64::from(t)*u64::from(n)));
    }}
    assert_eq!(counter_run(mode,1,1_000_000),Ok(1_000_000));
    assert_eq!(counter_run(mode,8,1_000_000),Ok(8_000_000));
}
fn fifo() {
    let q=BoundedQueue::new(3).unwrap();
    for _ in 0..20 {
        for id in [0,u64::MAX,17] {q.push(id).unwrap();}
        for id in [0,u64::MAX,17] {assert_eq!(q.pop().unwrap(),Some(id));}
    }
    q.push(42).unwrap();q.push(43).unwrap();q.close().unwrap();q.close().unwrap();
    assert_eq!(q.push(44),Err(QueueError::Closed));
    assert_eq!(q.pop().unwrap(),Some(42));assert_eq!(q.pop().unwrap(),Some(43));
    assert_eq!(q.pop().unwrap(),None);
    // Instâncias não compartilham estado; Drop só depois de reunir usuários.
    let other=BoundedQueue::new(1).unwrap();other.close().unwrap();assert_eq!(other.pop().unwrap(),None);
}
fn blocking(full:bool,closing:bool) {
    let q=Arc::new(BoundedQueue::new(1).unwrap());
    if full {q.push(91).unwrap();}
    let (entered,entered_rx)=mpsc::channel();let (done,done_rx)=mpsc::channel();
    let count=if closing {4} else {1};let mut threads=vec![];
    for _ in 0..count {
        let q=q.clone();let entered=entered.clone();let done=done.clone();
        threads.push(thread::spawn(move || {
            entered.send(()).unwrap();
            let result=if full {q.push(92).map(|()|None)} else {q.pop()};
            done.send(result).unwrap();
        }));
    }
    for _ in 0..count {entered_rx.recv_timeout(Duration::from_secs(2)).unwrap();}
    // Janela de observação; não prova que todas entraram em Condvar::wait.
    assert!(matches!(done_rx.recv_timeout(Duration::from_millis(50)),Err(mpsc::RecvTimeoutError::Timeout)));
    if closing {q.close().unwrap();}
    else if full {assert_eq!(q.pop().unwrap(),Some(91));}
    else {q.push(92).unwrap();}
    for _ in 0..count {
        let result=done_rx.recv_timeout(Duration::from_secs(2)).unwrap();
        let expected=if closing && full {Err(QueueError::Closed)}
                     else if full || closing {Ok(None)} else {Ok(Some(92))};
        assert_eq!(result,expected);
    }
    for t in threads {t.join().unwrap();}
    q.close().unwrap();
    if full {assert_eq!(q.pop().unwrap(),Some(if closing {91} else {92}));}
    assert_eq!(q.pop().unwrap(),None);
}
fn stress(capacity:usize,producers:usize,consumers:usize,items:usize) {
    let q=Arc::new(BoundedQueue::new(capacity).unwrap());
    let mut readers=vec![];let mut writers=vec![];
    for _ in 0..consumers {
        let q=q.clone();readers.push(thread::spawn(move || {
            let mut values=vec![];while let Some(id)=q.pop().unwrap() {values.push(id);}values
        }));
    }
    for producer in 0..producers {
        let q=q.clone();writers.push(thread::spawn(move || {
            for i in 0..items {q.push((producer*items+i) as u64).unwrap();}
        }));
    }
    for t in writers {t.join().unwrap();}q.close().unwrap();
    let mut all=vec![];for t in readers {all.extend(t.join().unwrap());}
    all.sort_unstable();assert_eq!(all,(0..(producers*items) as u64).collect::<Vec<_>>());
    assert_eq!(q.pop().unwrap(),None);
}
fn main() {
    let args:Vec<_>=std::env::args().collect();
    match args[1].as_str() {
        "invalid"=>invalid(),"mutex"=>counter(CounterMode::Mutex),"atomic"=>counter(CounterMode::Atomic),
        "fifo"=>fifo(),"empty"=>blocking(false,false),"full"=>blocking(true,false),
        "close-empty"=>blocking(false,true),"close-full"=>blocking(true,true),
        "ordered"=>ordered().unwrap(),
        "stress"=>stress(args[2].parse().unwrap(),args[3].parse().unwrap(),args[4].parse().unwrap(),args[5].parse().unwrap()),
        _=>panic!("caso desconhecido"),
    }
    println!("PASS");
}
