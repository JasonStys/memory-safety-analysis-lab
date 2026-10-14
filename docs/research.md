# Primary research and implementation choices

Researched 2026-10-14 by Jason Stys. Sources explain mechanisms, not permission to scan or execute third-party code.

- [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html): instrumented heap/stack/lifetime diagnostics and fail-fast handling informed explicit expected-signal assertions.
- [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html): signed arithmetic faults are a separate defect class, not confused with memory allocation limits.
- [LeakSanitizer](https://clang.llvm.org/docs/LeakSanitizer.html): process-end leak checks complement lifetime/RAII regressions; a clean default build is tested separately from the intentional leak.
- [LLVM libFuzzer](https://llvm.org/docs/LibFuzzer.html): actual coverage-guided input evolution, seeds and bounded campaigns, distinct from deterministic mutation tests.
- [Clang source coverage](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html): measured authored runtime line coverage with explicit file scope.
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines): RAII, explicit ownership and checked bounds inform repaired C++ interfaces.
- [Rust ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html): owned values/borrows plus compiler rejection examples, without unsafe escape hatches.

Authored MSL1 and generation-handle examples are teaching contracts, not imported network standards or externally validated vulnerability intelligence. FNV is noncryptographic; standard SHA256 provides byte provenance only. Tests and scanners demonstrate particular behavior, not universal correctness.
