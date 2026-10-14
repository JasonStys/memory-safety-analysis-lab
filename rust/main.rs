//! Jason Stys: bounded binary batch worker emitting only safe Rust parser metadata.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// parameter: io — line 21
// parameter: process — line 22
// fn: run — line 25
// binding: input — line 26
// parameter: io — line 27
// binding: cursor — line 34
// field/parameter: cursor — line 34
// binding: rows — line 35
// binding: length — line 40
// binding: output — line 52
// loop binding: row — line 54
// fn: main — line 60
// parameter: ExitCode — line 62
// parameter: ExitCode — line 64
// END CODE MAP
#![forbid(unsafe_code)]
use memory_safety_analysis_lab::{MAX_BYTES, parse, summary};
use std::{
    io::{self, Read, Write},
    process::ExitCode,
};
/// Validate the whole transport batch before emitting rows; no files, network or input code execute.
fn run() -> Result<(), &'static str> {
    let mut input = Vec::new();
    io::stdin()
        .take((8 * MAX_BYTES + 1) as u64)
        .read_to_end(&mut input)
        .map_err(|_| "input")?;
    if input.len() > 8 * MAX_BYTES {
        return Err("batch_limit");
    }
    let mut cursor: usize = 0;
    let mut rows = Vec::new();
    while cursor < input.len() {
        if rows.len() == 1000 || input.len() - cursor < 4 {
            return Err("batch_header");
        }
        let length = u32::from_le_bytes(
            input[cursor..cursor + 4]
                .try_into()
                .map_err(|_| "batch_header")?,
        ) as usize;
        cursor += 4;
        if length > MAX_BYTES || length > input.len() - cursor {
            return Err("batch_length");
        }
        rows.push(summary(parse(&input[cursor..cursor + length])));
        cursor += length;
    }
    let mut output = io::BufWriter::new(io::stdout().lock());
    writeln!(output, "MSAL\t1").map_err(|_| "output")?;
    for row in rows {
        writeln!(output, "{row}").map_err(|_| "output")?;
    }
    output.flush().map_err(|_| "output")
}
/// Exit 2 indicates batch/IO failure, distinct from a validated per-frame ERR row.
fn main() -> ExitCode {
    if run().is_ok() {
        ExitCode::SUCCESS
    } else {
        ExitCode::from(2)
    }
}
