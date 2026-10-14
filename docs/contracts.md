# Data, ownership and process contracts

Author: Jason Stys. MSL1 is an authored teaching format, not a network/industry standard.

## MSL1 frame

Four ASCII magic bytes MSL1, then little-endian u16 record count ≤128. Each record has tag u8, little-endian u16 payload length ≤256, then exactly that many bytes. Tag 1 requires four bytes (opaque integer encoding), tag 2 requires nonempty printable ASCII 32–126, tag 3 permits any bytes including an empty blob. No trailing bytes. Every parser checks ≤1 MiB before work/allocation. A maximally valid frame is 6 + 128 × 259 = 33,158 bytes; the larger cap bounds malformed-input handling.

Stable frame codes: byte_limit, header, magic, record_limit, record_header, tag, payload_limit, payload_truncated, integer_width, text, trailing. Failure ordering is identical in all three independently written implementations.

Native stdin is a bounded sequence of little-endian u32 frame lengths and frame bytes: ≤1000 frames, ≤1 MiB per frame and ≤8 MiB total. Both workers validate the entire transport before emitting any rows. A malformed later transport record cannot make earlier results appear fully valid. Native output starts MSAL TAB 1, then ERR/code or OK/count/payload_bytes/u64_fingerprint rows. Python enforces exact count/version, safe error allowlist, ASCII unsigned numbers, count/size/hash ranges and ≤128 KiB output.

FNV-1a fingerprints intentionally wrap unsigned 64-bit arithmetic; they are **not cryptographic hashes, collision-free identity or authentication**. Standard-library SHA256 records the exact input bytes reviewed, not a signed custody chain.

## Memory and lifetime invariants

C++ Record owns its vector; Rust Record owns its Vec. Input spans/slices cannot escape the decoder. Cursor advances check remaining length with subtraction before constructing a view. Extent checks width>0 and count≤limit/width before multiplication. Owned copies survive source disposal.

Arena stores ≤128 owned strings of ≤1024 bytes each. A Handle belongs to its originating arena and carries index+generation. Gets return a copy; erase invalidates exactly once; reuse increments generation, and wrap permanently retires the slot instead of reviving a stale handle. Handles from different arenas are not distinguishable, and shared-thread access requires external synchronization. No arbitrary pointers/free operations are accepted.

## Process and reporting limits

Python invokes only fixed repository-built C++/Rust paths, with no shell and a 15-second native deadline. Input is data, never source or executable. Batch/output cardinality and byte caps bound work, but are not OS memory/CPU isolation. A trusted replaced executable or hostile local administrator is outside the model.

Default reports export metadata, expected/observed results and hashes; payloads and input filenames are absent. Exclusive output creation refuses overwrite/symlink replacement. POSIX files are owner-only; Windows relies on inherited user-directory NTFS ACLs. Reports/diagnostics are not encrypted. New output folders can remain partial after an IO failure; do not call them complete reviews.
