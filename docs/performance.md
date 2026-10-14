# Complexity and performance methodology

Author: Jason Stys. Finite measurements are not claims that one language is universally faster.

For B bounded input bytes and R≤128 records, parsing, validation and FNV inspection are O(B+R). Owned payload storage is O(B+R), but the valid protocol only needs ≤33,158 bytes per frame. The transport holds ≤8 MiB plus ≤1000 short metadata rows. Python reference/hash work is also linear; independent subprocess startup can dominate tiny inputs.

Arena lookup/erase are O(1) index/generation checks plus O(value length) for returned copies/destruction. Insert scans ≤128 slots, O(S+value length); it trades a small bounded scan for simple auditable ownership. Extent uses a constant-time division guard before multiplication. No unbounded allocation, string-size inference or raw owning pointer is accepted.

scripts/benchmark.py uses identical batches of 100 frames, each with 1 / 32 / 128 records and fixed 112-byte synthetic payloads. It warms each Release implementation once and records seven wall-clock samples per workload, checking expected metadata every time. Startup, stdin/stdout framing, parsing/hash and Python metadata validation are included; generation, network, sanitizer and coverage overhead are excluded. This is not a pure function benchmark, peak-memory profile or language-wide comparison.

Raw seconds, medians, OS, architecture, Python version and measurement time are recorded; compiler identities are printed in native build logs. Shared-runner timing is observation, not a brittle arbitrary throughput threshold. Cardinality, deadline and correctness are enforceable gates. The 1 GiB libFuzzer RSS limit is a campaign limit, not a measured app-memory guarantee.
