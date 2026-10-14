//! Jason Stys: safe Rust parser, checked length arithmetic and generation-safe owned handles.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// const: MAX_BYTES — line 72
// field/parameter: _BYTES — line 72
// const: MAX_RECORDS — line 73
// field/parameter: _RECORDS — line 73
// struct: Record — line 76
// field/parameter: tag — line 77
// field/parameter: payload — line 78
// field/parameter: count — line 81
// field/parameter: limit — line 81
// field/parameter: width — line 81
// fn: extent — line 81
// field/parameter: input — line 89
// field/parameter: limit — line 89
// fn: copy — line 89
// field/parameter: input — line 93
// field/parameter: position — line 93
// fn: word — line 93
// parameter: usize — line 94
// field/parameter: input — line 97
// fn: parse — line 97
// binding: count — line 107
// binding: records — line 111
// binding: cursor — line 112
// loop binding: _ — line 113
// binding: tag — line 117
// binding: length — line 118
// binding: view — line 129
// field/parameter: payload — line 138
// parameter: payload — line 138
// field/parameter: records — line 148
// fn: fingerprint — line 148
// binding: hash — line 149
// field/parameter: hash — line 149
// loop binding: record — line 150
// loop binding: byte — line 152
// field/parameter: result — line 159
// fn: summary — line 159
// struct: Handle — line 175
// field/parameter: index — line 176
// field/parameter: generation — line 177
// struct: Slot — line 180
// field/parameter: generation — line 181
// parameter: generation — line 181
// field/parameter: value — line 182
// parameter: value — line 182
// struct: Arena — line 186
// field/parameter: slots — line 187
// parameter: slots — line 187
// field/parameter: value — line 191
// fn: insert — line 191
// loop binding: index — line 195
// loop binding: slot — line 195
// field/parameter: generation — line 200
// parameter: generation — line 200
// parameter: generation — line 208
// field/parameter: value — line 209
// parameter: value — line 209
// field/parameter: index — line 212
// parameter: index — line 212
// parameter: generation — line 213
// field/parameter: handle — line 217
// fn: get — line 217
// binding: slot — line 218
// field/parameter: handle — line 226
// fn: erase — line 226
// binding: slot — line 227
// mod: tests — line 239
// END CODE MAP
#![forbid(unsafe_code)]
pub const MAX_BYTES: usize = 1024 * 1024;
pub const MAX_RECORDS: usize = 128;
/// Each record owns its payload; no borrowed input pointer escapes parsing.
#[derive(Debug, PartialEq, Eq)]
pub struct Record {
    pub tag: u8,
    pub payload: Vec<u8>,
}
/// Guard multiplication before allocation; zero width is not a valid element size.
pub fn extent(count: usize, width: usize, limit: usize) -> Option<usize> {
    if width == 0 || count > limit / width {
        None
    } else {
        count.checked_mul(width)
    }
}
/// Return a bounded independently owned copy of the input bytes.
pub fn copy(input: &[u8], limit: usize) -> Option<Vec<u8>> {
    (input.len() <= limit).then(|| input.to_vec())
}
/// Read only after callers established that two bytes remain.
fn word(input: &[u8], position: usize) -> usize {
    usize::from(input[position]) | (usize::from(input[position + 1]) << 8)
}
/// Decode a complete bounded MSL1 packet; stable codes match the independent C++ implementation.
pub fn parse(input: &[u8]) -> Result<Vec<Record>, &'static str> {
    if input.len() > MAX_BYTES {
        return Err("byte_limit");
    }
    if input.len() < 6 {
        return Err("header");
    }
    if &input[..4] != b"MSL1" {
        return Err("magic");
    }
    let count = word(input, 4);
    if count > MAX_RECORDS {
        return Err("record_limit");
    }
    let mut records = Vec::with_capacity(count);
    let mut cursor = 6;
    for _ in 0..count {
        if input.len() - cursor < 3 {
            return Err("record_header");
        }
        let tag = input[cursor];
        let length = word(input, cursor + 1);
        cursor += 3;
        if !(1..=3).contains(&tag) {
            return Err("tag");
        }
        if length > 256 {
            return Err("payload_limit");
        }
        if length > input.len() - cursor {
            return Err("payload_truncated");
        }
        let view = &input[cursor..cursor + length];
        if tag == 1 && length != 4 {
            return Err("integer_width");
        }
        if tag == 2 && (length == 0 || !view.iter().all(|byte| (32..=126).contains(byte))) {
            return Err("text");
        }
        records.push(Record {
            tag,
            payload: view.to_vec(),
        });
        cursor += length;
    }
    if cursor != input.len() {
        return Err("trailing");
    }
    Ok(records)
}
/// FNV-1a wrapping is intentional noncryptographic metadata, not signed overflow or authentication.
pub fn fingerprint(records: &[Record]) -> u64 {
    let mut hash: u64 = 14695981039346656037;
    for record in records {
        hash = (hash ^ u64::from(record.tag)).wrapping_mul(1099511628211);
        for byte in &record.payload {
            hash = (hash ^ u64::from(*byte)).wrapping_mul(1099511628211);
        }
    }
    hash
}
/// Export only bounded metadata/errors, not synthetic or user-provided payload contents.
pub fn summary(result: Result<Vec<Record>, &'static str>) -> String {
    match result {
        Err(code) => format!("ERR\t{code}"),
        Ok(records) => format!(
            "OK\t{}\t{}\t{}",
            records.len(),
            records
                .iter()
                .map(|value| value.payload.len())
                .sum::<usize>(),
            fingerprint(&records)
        ),
    }
}
/// Handle generations reject stale lookups/double releases without exposing addresses.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Handle {
    pub index: usize,
    pub generation: u64,
}
/// Owned optional values; a zero generation is retired permanently after wrap.
struct Slot {
    generation: u64,
    value: Option<String>,
}
/// Bounded owned values; retrieval clones rather than returning a reference whose lifetime is unclear.
#[derive(Default)]
pub struct Arena {
    slots: Vec<Slot>,
}
impl Arena {
    /// Insert at most 1024 bytes in at most 128 slots; retired generations are never reused.
    pub fn insert(&mut self, value: &str) -> Option<Handle> {
        if value.len() > 1024 {
            return None;
        }
        for (index, slot) in self.slots.iter_mut().enumerate() {
            if slot.value.is_none() && slot.generation != 0 {
                slot.value = Some(value.to_owned());
                return Some(Handle {
                    index,
                    generation: slot.generation,
                });
            }
        }
        if self.slots.len() == MAX_RECORDS {
            return None;
        }
        self.slots.push(Slot {
            generation: 1,
            value: Some(value.to_owned()),
        });
        Some(Handle {
            index: self.slots.len() - 1,
            generation: 1,
        })
    }
    /// Copy only a live matching slot; invalid indexes/generations remain controlled misses.
    pub fn get(&self, handle: Handle) -> Option<String> {
        let slot = self.slots.get(handle.index)?;
        if slot.generation == handle.generation {
            slot.value.clone()
        } else {
            None
        }
    }
    /// Invalidate exactly once; checked_add retires on overflow rather than reviving stale handles.
    pub fn erase(&mut self, handle: Handle) -> bool {
        let Some(slot) = self.slots.get_mut(handle.index) else {
            return false;
        };
        if slot.generation != handle.generation || slot.value.is_none() {
            return false;
        }
        slot.value = None;
        slot.generation = slot.generation.checked_add(1).unwrap_or(0);
        true
    }
}
#[cfg(test)]
mod tests;
