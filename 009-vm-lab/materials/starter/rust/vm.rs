// SPDX-License-Identifier: MIT
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TraceRow {
    pub pc: usize,
    pub opcode: String,
    pub stack: Vec<i32>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct State {
    pub pc: usize,
    pub stack: Vec<i32>,
    pub variables: [i32; 8],
    pub steps: usize,
    pub trace: Vec<TraceRow>,
    // None significa halted; Some contém um dos códigos do contrato.
    pub error: Option<&'static str>,
}

#[derive(Debug)]
pub struct InvalidBudget;

pub fn run(_source: &str, _budget: i64) -> Result<State, InvalidBudget> {
    // TODO: valide budget; parse e valide o programa inteiro antes de executar.
    // TODO: estado inicial, fetch/dispatch, checked_add/checked_sub, trace.
    // Falha de uma instrução preserva seu estado anterior e não conta um step.
    todo!("implemente validação, dispatch e transições da VM")
}
