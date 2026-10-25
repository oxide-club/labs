// SPDX-License-Identifier: MIT
use atomics_lab::*;
fn sequential() {
    for v in [Variant::Weak, Variant::Publish, Variant::Strong] {
        let s=State::new(); assert_eq!(s.try_read(v),None,"initial");
        s.publish(v); assert_eq!(s.try_read(v),Some(42),"published");
    }
}
#[test]
fn sequential_contract() {
    #[cfg(feature="model")] loom::model(sequential);
    #[cfg(not(feature="model"))] sequential();
}
#[cfg(feature="model")]
fn explore(v: Variant) {
    // Instrumentação externa: apenas o consumidor acessa estes contadores std.
    // O produtor nunca os lê. Nenhuma operação é acrescentada ao estado modelado.
    use std::sync::{Arc as HostArc, atomic::{AtomicUsize as HostCounter, Ordering as HostOrder}};
    let counts=HostArc::new([HostCounter::new(0),HostCounter::new(0),HostCounter::new(0),HostCounter::new(0)]);
    let observed=counts.clone();
    let mut b=loom::model::Builder::new();
    b.max_threads=2; b.max_branches=1000; b.preemption_bound=None;
    b.max_permutations=None; b.max_duration=None; b.checkpoint_file=None;
    b.expect_explicit_explore=false; b.location=true; b.log=false;
    println!("MODEL_CONFIG variant={v:?} loom=0.7.2 max_threads=2 max_branches=1000 preemption_bound=none max_permutations=none max_duration=none consumer_before_join=true");
    let exploration=std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| b.check(move || {
        let s=Arc::new(State::new()); let p=s.clone();
        let producer=thread::spawn(move || p.publish(v));
        let seen=s.try_read(v); // Retorno capturado ANTES de join.
        producer.join().unwrap();
        // Contagem e impressão depois de join, usando somente o retorno já capturado.
        let bucket=match seen {None=>0,Some(42)=>1,Some(0)=>2,_=>3};
        observed[bucket].fetch_add(1,HostOrder::Relaxed);
        let execution=observed.iter().map(|n|n.load(HostOrder::Relaxed)).sum::<usize>();
        println!("MODEL_OBSERVATION variant={v:?} execution={execution} observed={seen:?} captured_before_join=true");
        match seen {
            None|Some(42)=>{},
            Some(0)=>{
                eprintln!("RETURN_DIAGNOSTIC variant={v:?} observed=Some(0) inferred_ready=true inferred_data=0");
                panic!("PUBLICATION_VIOLATION ready=true data=0 observed=Some(0)");
            },
            other=>panic!("UNEXPECTED_VALUE {:?}",other)
        }
    })));
    let n=counts.each_ref().map(|c|c.load(HostOrder::Relaxed));
    let stop=if exploration.is_ok(){"complete"}else{"interrupted"};
    println!("MODEL_SUMMARY variant={v:?} executions={} None={} Some42={} Some0={} Other={} stop={stop}",n.iter().sum::<usize>(),n[0],n[1],n[2],n[3]);
    if let Err(payload)=exploration {std::panic::resume_unwind(payload);}
    if !matches!(v,Variant::Weak) {
        assert!(n[0]>0 && n[1]>0,"MODEL_EVIDENCE_MISSING: necessário observar None e Some(42)");
    }
}
#[cfg(feature="model")]
#[test] fn weak_counterexample() { explore(Variant::Weak) }
#[cfg(feature="model")]
#[test] fn release_acquire() { explore(Variant::Publish) }
#[cfg(feature="model")]
#[test] fn sequential_consistency() { explore(Variant::Strong) }

#[cfg(not(feature="model"))]
#[test]
fn local_observations() {
    for v in [Variant::Weak, Variant::Publish, Variant::Strong] {
        let mut counts=[0usize;3];
        for _ in 0..1000 {
            let s=Arc::new(State::new()); let p=s.clone();
            let producer=thread::spawn(move || p.publish(v));
            let seen=s.try_read(v);
            producer.join().unwrap();
            match seen { None=>counts[0]+=1, Some(42)=>counts[1]+=1,
                Some(0) if matches!(v,Variant::Weak)=>counts[2]+=1,
                other=>panic!("UNEXPECTED_VALUE {other:?}") }
        }
        println!("STD {v:?} samples=1000 None={} Some42={} Some0={}",counts[0],counts[1],counts[2]);
    }
}
