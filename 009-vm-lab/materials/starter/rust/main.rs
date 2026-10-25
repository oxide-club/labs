// SPDX-License-Identifier: MIT
// Adaptador de verificação; não faz parte do mecanismo da VM.
mod vm;
use std::io::{self, Read};

fn quote(value: &str) -> String {
    let mut out = String::from("\"");
    for c in value.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            c if c < ' ' => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

fn json(state: &vm::State) -> String {
    let trace = state.trace.iter().map(|row| {
        format!("{{\"pc\":{},\"opcode\":{},\"stack\":{:?}}}",
                row.pc, quote(&row.opcode), row.stack)
    }).collect::<Vec<_>>().join(",");
    format!("{{\"status\":{},\"error\":{},\"pc\":{},\"stack\":{:?},\"variables\":{:?},\"steps\":{},\"trace\":[{}]}}",
        quote(if state.error.is_some() { "error" } else { "halted" }),
        state.error.map(quote).unwrap_or_else(|| "null".into()),
        state.pc, state.stack, state.variables, state.steps, trace)
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let budget = if args.len() == 2 { args[1].parse::<i64>().ok() } else { None };
    let Some(budget) = budget else {
        eprintln!("budget deve ser inteiro decimal");
        std::process::exit(2);
    };
    let mut source = String::new();
    if let Err(error) = io::stdin().read_to_string(&mut source) {
        eprintln!("stdin: {error}");
        std::process::exit(1);
    }
    match vm::run(&source, budget) {
        Ok(state) => println!("{}", json(&state)),
        Err(_) => { eprintln!("budget fora de 1..10000"); std::process::exit(2); }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn transport_preserves_fields_and_escapes() {
        assert_eq!(quote("\"\\\n"), "\"\\\"\\\\\\u000a\"");
        let state = vm::State { pc: 0, stack: vec![], variables: [0; 8], steps: 0,
                                trace: vec![], error: Some("invalid_program") };
        assert_eq!(json(&state), "{\"status\":\"error\",\"error\":\"invalid_program\",\"pc\":0,\"stack\":[],\"variables\":[0, 0, 0, 0, 0, 0, 0, 0],\"steps\":0,\"trace\":[]}");
    }
}
