//! Jason Stys: expected E0382 exercise; rustc must reject use after moving ownership.
/// No executable is produced or run; the earlier move consumes the owned value.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// fn: main — line 8
// binding: value — line 9
// binding: owner — line 10
// END CODE MAP
fn main() {
    let value = String::from("synthetic");
    let owner = value;
    println!("{owner} {value}");
}
