//! Jason Stys: expected E0502 exercise; rustc must reject mutation during a live shared borrow.
/// The shared view is used after attempted mutation, preserving the compile-time lifetime conflict.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// fn: main — line 8
// binding: value — line 9
// binding: view — line 10
// END CODE MAP
fn main() {
    let mut value = String::from("synthetic");
    let view = &value;
    value.push('!');
    println!("{view}");
}
