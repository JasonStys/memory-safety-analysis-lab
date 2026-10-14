# Defect-to-fix teaching guide

Author: Jason Stys. These are tiny synthetic errors, not findings in a real organization's software.

| Fault specimen | Root cause | Safe replacement / regression | Tool assertion |
| --- | --- | --- | --- |
| Heap over-read, CWE-125 | Index reaches allocation end | Validated remaining length before span/slice access; truncated/header/payload tests | ASan heap-buffer-overflow |
| Stack over-read, CWE-125 | Local-array boundary ignored | Owned bounded records instead of unbounded fixed-buffer indexing | ASan stack-buffer-overflow |
| Use-after-free, CWE-416 | Borrow outlives deleted owner | RAII owner and copied reads; erased/stale handle lookup misses | ASan heap-use-after-free |
| Double-free, CWE-415 | Same allocation released twice | Arena invalidates once and rejects repeat erase; no manual delete in safe implementation | ASan attempting double-free |
| Leak, CWE-401 | Allocation loses owner | Vector/string/Vec ownership and destructor cleanup; sanitized safe tests exit cleanly | LSan detected memory leaks |
| Signed overflow, CWE-190 | Arithmetic before validating extent | Division guard and Rust checked multiplication; max-size count boundary regression | UBSan signed integer overflow |
| Moved Rust value | Ownership consumed then reused | Compiler rejects invalid move; owned snapshots used safely | rustc E0382 |
| Shared Rust borrow conflict | Mutation overlaps later shared read | Compiler rejects invalid lifetime; owned copy or scoped borrow | rustc E0502 |

An expected defect makes the **assertion** pass only when the correct sanitizer/compiler diagnostic appears and the child fails. A clean exit or unrelated compiler/runtime failure fails the gate. Do not call the deliberately faulty programs safe or treat generic nonzero exits as proof a tool detected the intended error.

Compile-time ownership helps with memory lifetimes; it does not automatically validate a binary schema, application authorization or all logical errors. Sanitizers observe executed instrumented paths and cannot prove absence of defects elsewhere. These examples demonstrate general remediation patterns, not line-for-line production patch recommendations.
