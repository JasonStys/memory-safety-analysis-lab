//! Jason Stys: native Rust parser/ownership/bounds invariants and deterministic mutation exercise.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// field/parameter: payload — line 49
// field/parameter: tag — line 49
// fn: record — line 49
// binding: data — line 50
// fn: parser_boundaries — line 58
// loop binding: data — line 59
// loop binding: expected — line 59
// binding: data — line 74
// binding: data — line 77
// fn: valid_and_prefixes — line 83
// loop binding: data — line 84
// loop binding: size — line 86
// fn: arithmetic_and_copy — line 98
// binding: source — line 104
// binding: result — line 105
// fn: arena_lifetimes — line 113
// binding: arena — line 114
// parameter: index — line 117
// parameter: generation — line 118
// parameter: index — line 123
// parameter: generation — line 124
// binding: source — line 127
// binding: first — line 128
// binding: snapshot — line 130
// binding: replacement — line 134
// loop binding: _ — line 141
// fn: generation_wrap — line 148
// binding: arena — line 149
// field/parameter: generation — line 151
// parameter: generation — line 151
// field/parameter: value — line 152
// parameter: value — line 152
// parameter: index — line 155
// field/parameter: generation — line 156
// parameter: generation — line 156
// fn: mutation_exercise — line 163
// binding: seed — line 164
// binding: state — line 165
// field/parameter: state — line 165
// loop binding: iteration — line 166
// binding: data — line 170
// binding: position — line 171
// binding: _ — line 176
// END CODE MAP
use super::*;
/// Independent native single-record encoder.
fn record(tag: u8, payload: &[u8]) -> Vec<u8> {
    let mut data = b"MSL1\x01\x00".to_vec();
    data.push(tag);
    data.extend((payload.len() as u16).to_le_bytes());
    data.extend(payload);
    data
}
#[test]
/// Every error code is an explicit regression; malformed inputs never require unsafe indexing.
fn parser_boundaries() {
    for (data, expected) in [
        (vec![], "header"),
        (vec![0; MAX_BYTES + 1], "byte_limit"),
        (vec![0; 6], "magic"),
        (b"MSL1\x81\x00".to_vec(), "record_limit"),
        (b"MSL1\x01\x00".to_vec(), "record_header"),
        (record(0, &[]), "tag"),
        (record(3, &[0; 257]), "payload_limit"),
        (record(1, &[]), "integer_width"),
        (record(2, &[]), "text"),
        (record(2, &[0]), "text"),
        (record(2, &[127]), "text"),
    ] {
        assert_eq!(parse(&data).unwrap_err(), expected);
    }
    let mut data = record(3, &[1]);
    data.pop();
    assert_eq!(parse(&data).unwrap_err(), "payload_truncated");
    let mut data = record(3, &[]);
    data.push(0);
    assert_eq!(parse(&data).unwrap_err(), "trailing");
}
#[test]
/// Valid tags, root empty packet and every incomplete prefix preserve the shared contract.
fn valid_and_prefixes() {
    for data in [record(1, &[0, 1, 2, 3]), record(2, b" ~"), record(3, &[])] {
        assert!(summary(parse(&data)).starts_with("OK\t1\t"));
        for size in 0..data.len() {
            assert!(parse(&data[..size]).is_err());
        }
    }
    assert_eq!(
        summary(parse(b"MSL1\0\0")),
        "OK\t0\t0\t14695981039346656037"
    );
    assert_eq!(summary(Err("text")), "ERR\ttext");
}
#[test]
/// Arithmetic is checked before allocating; copies remain valid after source disposal.
fn arithmetic_and_copy() {
    assert_eq!(extent(0, 4, 16), Some(0));
    assert_eq!(extent(4, 4, 16), Some(16));
    assert_eq!(extent(5, 4, 16), None);
    assert_eq!(extent(1, 0, 16), None);
    assert_eq!(extent(usize::MAX, 2, 1024), None);
    let source = vec![1, 2, 3];
    let result = copy(&source, 3).unwrap();
    drop(source);
    assert_eq!(result, vec![1, 2, 3]);
    assert_eq!(copy(&result, 2), None);
    assert_eq!(copy(&[], 0), Some(vec![]));
}
#[test]
/// Stale, invalid, repeated release and full-capacity behavior avoids dangling pointers and double free.
fn arena_lifetimes() {
    let mut arena = Arena::default();
    assert_eq!(
        arena.get(Handle {
            index: 999,
            generation: 1
        }),
        None
    );
    assert!(!arena.erase(Handle {
        index: 999,
        generation: 1
    }));
    assert!(arena.insert(&"x".repeat(1025)).is_none());
    let mut source = "owned".to_owned();
    let first = arena.insert(&source).unwrap();
    source.clear();
    let snapshot = arena.get(first).unwrap();
    assert!(arena.erase(first));
    assert_eq!(arena.get(first), None);
    assert!(!arena.erase(first));
    let replacement = arena.insert("new").unwrap();
    assert_eq!(first.index, replacement.index);
    assert_ne!(first.generation, replacement.generation);
    assert_eq!(arena.get(first), None);
    assert!(!arena.erase(first));
    assert_eq!(arena.get(replacement).as_deref(), Some("new"));
    assert_eq!(snapshot, "owned");
    for _ in 1..MAX_RECORDS {
        assert!(arena.insert("").is_some());
    }
    assert!(arena.insert("full").is_none());
}
#[test]
/// A forced maximum generation retires safely; private test access does not expose mutation in the API.
fn generation_wrap() {
    let mut arena = Arena::default();
    arena.slots.push(Slot {
        generation: u64::MAX,
        value: Some("last".to_owned()),
    });
    assert!(arena.erase(Handle {
        index: 0,
        generation: u64::MAX
    }));
    assert_eq!(arena.slots[0].generation, 0);
    assert_eq!(arena.insert("next").unwrap().index, 1);
}
#[test]
/// Reproducible mutations exercise native parsing; coverage-guided fuzzing is separately performed in C++.
fn mutation_exercise() {
    let seed = record(2, b"synthetic");
    let mut state: u64 = 0x7481_a20c_3f59_401d;
    for iteration in 0..100_000 {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        let mut data = seed.clone();
        let position = state as usize % data.len();
        data[position] = (state >> 32) as u8;
        if iteration % 3 == 0 {
            data.truncate(position);
        }
        let _ = parse(&data);
    }
}
