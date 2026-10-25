// SPDX-License-Identifier: MIT
use dispatch_core::*;
use std::cell::RefCell;
#[test]
fn vectors() {
    let cases: &[(&[u64],u64,u64)] = &[
        (&[],0,0), (&[0,1,2,u64::MAX],30,6),
        (&[9,9,9],48,81), (&[u64::MAX],6,u64::MAX-2),
        (&[1<<63,1<<63],14,0)];
    for &(input,add,mul) in cases {
        assert_eq!(generic(input,&Add{delta:7}),add);
        assert_eq!(dynamic(input,&Add{delta:7}),add);
        assert_eq!(enumerated(input,&Operation::Add(Add{delta:7})),add);
        assert_eq!(generic(input,&Mul{factor:3}),mul);
        assert_eq!(dynamic(input,&Mul{factor:3}),mul);
        assert_eq!(enumerated(input,&Operation::Mul(Mul{factor:3})),mul);
    }
}
#[test]
fn parameters_and_order() {
    assert_eq!(generic(&[1,2],&Add{delta:11}),25);
    assert_eq!(dynamic(&[1,2],&Mul{factor:11}),33);
    assert_eq!(enumerated(&[1,2],&Operation::Add(Add{delta:11})),25);
    assert_eq!(enumerated(&[1,2],&Operation::Mul(Mul{factor:11})),33);
    struct Trace(RefCell<Vec<u64>>);
    impl Op for Trace { fn apply(&self,x:u64)->u64 {self.0.borrow_mut().push(x); x} }
    let input=[4,1,4,9]; let op=Trace(RefCell::new(Vec::new()));
    assert_eq!(generic(&input,&op),18); assert_eq!(*op.0.borrow(),input);
    op.0.borrow_mut().clear();
    assert_eq!(dynamic(&input,&op),18); assert_eq!(*op.0.borrow(),input);
}
