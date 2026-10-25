// SPDX-License-Identifier: MIT
#[cfg(feature="local-core")]
#[path="../../core/src/lib.rs"]
mod local_core;
#[cfg(feature="local-core")]
use local_core::*;
#[cfg(not(feature="local-core"))]
use dispatch_core::*;
use std::{hint::black_box, time::Instant};
fn main() {
    if let Err(error)=run() { eprintln!("PREPARACAO: {error}"); std::process::exit(2); }
}
fn run() -> Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().collect();
    if args.len()!=3 { return Err("uso: dispatch-harness DATASET.txt REPETICOES".into()); }
    let repetitions:usize=args[2].parse()?;
    if !(2..=10000).contains(&repetitions) { return Err("repetições: 2..10000".into()); }
    let input:Vec<u64>=std::fs::read_to_string(&args[1])?.lines()
        .map(str::parse).collect::<Result<_,_>>()?;
    let add=Add{delta:7}; let mul=Mul{factor:3};
    let ea=Operation::Add(Add{delta:7}); let em=Operation::Mul(Mul{factor:3});
    // Seleção, construção e alocação ocorrem antes de iniciar o relógio.
    // O valor concreto fica opaco antes da coerção; a vtable continua conhecida.
    let work:[(&str, &str, Box<dyn Fn()->u64>);6]=[
        ("add","generic",Box::new(||generic(black_box(&input),black_box(&add)))),
        ("add","dynamic",Box::new(||dynamic(black_box(&input),black_box(&add) as &dyn Op))),
        ("add","enum",Box::new(||enumerated(black_box(&input),black_box(&ea)))),
        ("mul","generic",Box::new(||generic(black_box(&input),black_box(&mul)))),
        ("mul","dynamic",Box::new(||dynamic(black_box(&input),black_box(&mul) as &dyn Op))),
        ("mul","enum",Box::new(||enumerated(black_box(&input),black_box(&em))))];
    // Oráculo agregado: não reutiliza apply nem os processadores.
    let total=input.iter().fold(0u64,|sum,x|sum.wrapping_add(*x));
    let expected=[total.wrapping_add((input.len() as u64).wrapping_mul(7)),total.wrapping_mul(3)];
    for _ in 0..2 { for (i,(_,_,f)) in work.iter().enumerate() {
        assert_eq!(black_box(f()),expected[i/3],"equivalência antes de medir");
    }}
    let mut samples=Vec::with_capacity(repetitions*6);
    for repetition in 0..repetitions {
        for offset in 0..6 {
            let index=(offset+repetition)%6;
            let (_,_,f)=&work[index];
            let start=Instant::now();
            let checksum=black_box(f());
            let ns=start.elapsed().as_nanos();
            assert_eq!(checksum,expected[index/3],"equivalência durante medição");
            samples.push((index,repetition,ns,checksum));
        }
    }
    println!("operation,variant,repetition,n,ns,checksum");
    for (i,rep,ns,checksum) in samples {
        println!("{},{},{rep},{},{ns},{checksum}",work[i].0,work[i].1,input.len());
    }
    Ok(())
}
