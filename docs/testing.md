# Testing strategy and acceptance gates

Author: Jason Stys. Separate expected-defect assertions from clean repaired-runtime tests.

The safe C++ invariant suite uses always-active checks, not assert() disabled by NDEBUG. It covers every parser code, all valid tags, integer width/text boundaries, copying independent ownership, multiplication limits, invalid/stale/double-erased handles and full capacity. Rust has equivalent native regressions, explicit generation-wrap retirement and 100,000 deterministic mutations per debug/release suite.

243 deterministic corpus cases include valid/max-record frames, labeled failures, every partial seed prefix and fixed-seed mutations. Actual C++/Rust workers must agree with independent Python metadata. A Hypothesis property runs 200 reproducible arbitrary ≤4096-byte cases through all three. Report privacy, no-overwrite behavior, exact hashes, deadlines/missing binaries/native failures and transport corruption have integration tests.

Linux assurance first requires six specific ASan/UBSan/LSan diagnostics from allowlisted faulty specimens and two exact rustc error codes. It then runs the corrected C++ unit suite and corpus under ASan/UBSan with leak checks enabled. Source coverage gates ≥95% combined **line** coverage for native/safe.cpp and native/main.cpp; headers, test/fuzz harness and deliberate specimens are not advertised as covered application modules. Branch percentages are not inferred from line coverage.

libFuzzer performs 20,000 coverage-guided safe-parser runs with seed 12345, ≤65,536-byte fuzz cases, a 2-second per-input timeout and 1 GiB RSS cap. Crashes/timeouts/leaks fail CI and stay in local generated outputs; nothing is uploaded. Rust's deterministic mutation exercise is not advertised as a coverage-guided Rust fuzz campaign. Finite campaigns are not safety proofs.

All four Python runtime modules are included in the ≥95% combined statement/branch gate. Ruff, strict mypy, Rust fmt/clippy, C++ warning-as-error builds, Clang 18 formatting, full locked graph audit, full-history Gitleaks, actionlint and exact symbol/file/privacy/link gates are required. CI matrices cover Linux Python 3.12/3.14, Windows 3.14 and macOS 3.14.

CodeQL security-extended analyzes Python and manually built safe C++; faulty specimens are not built there, and no repaired-code alerts are suppressed. Rust has explicit native/ownership/tool checks, not a claimed Rust CodeQL scan. Windows local results and hosted Linux sanitizer/coverage/fuzz evidence are distinguished in [validation](reports/validation.md). Each final-main job must pass, including documentation changes.
