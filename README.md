# Memory Safety Analysis Lab

[![Validate](https://github.com/JasonStys/memory-safety-analysis-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/memory-safety-analysis-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/memory-safety-analysis-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/memory-safety-analysis-lab/actions/workflows/codeql.yml)

Created by **Jason Stys** — [GitHub](https://github.com/JasonStys) · [LinkedIn/contact](https://www.linkedin.com/in/jason-stys-31b30b351/).

A defensive portfolio lab connecting **real memory-error diagnostics** to **safe C++20 fixes, Rust ownership equivalents and measurable regression evidence**. The default app compares a bounded synthetic binary decoder in C++, Rust and independent Python, and creates private JSON/inert HTML reports.

This is a teaching/assurance lab, **not an arbitrary-code runner, universal vulnerability scanner, exploit kit or proof of memory safety**. No network targets, capture drivers, cloud resources, accounts or telemetry. The explicitly faulty specimens are not part of the default build/app and are executed only by the opt-in Linux teaching harness.

## Major features

- **C++ fixes:** owned vectors/strings, borrowed spans used within validated bounds, checked length multiplication, generation-tagged handles rejecting stale lookups and double release, RAII cleanup and copied lifetime-independent values.
- **Rust equivalents:** the same decoding/handle contracts with checked arithmetic and forbidden unsafe code; separate compile-fail exercises prove ownership/borrowing errors are rejected.
- **Explainable failures:** six tiny synthetic faulty C++ cases cover heap/stack over-read, use-after-free, double-free, leak and signed length-arithmetic overflow. CI requires the specific sanitizer signal and nonzero exit, not just any crash.
- **Three-way validation:** 243 deterministic corpus cases plus 200 Hypothesis-generated arbitrary byte cases run through actual C++/Rust workers and Python's independent reference.
- **Dynamic assurance:** safe runtime ASan/UBSan/LSan checks, ≥95% C++ runtime line-coverage gate, and 20,000 coverage-guided libFuzzer runs on the safe parser. Rust also has 100,000 deterministic mutation cases per debug/release profile.
- **Reproducible evidence:** input SHA256, exact expected/observed metadata, scoped tool reports, release benchmarks, full file/symbol inventories and cross-platform CI. Reports never export payloads or source paths.

## Quick start

Requires Python 3.12–3.14, CMake ≥3.24, a C++20 compiler and Rust 1.98.1 through rustup. Windows uses Visual Studio C++ build tools compatible with installed CMake (2022 or newer); Linux/macOS use their installed GCC/Clang toolchain. No Python runtime dependencies.

From the repository root:

~~~text
python scripts/build.py
python -m msal.cli --output out/review
~~~

Open the generated report.html locally; report.json provides machine-readable expected/observed results. Each output directory must be new. To review one **MSL1 data file**, not source/executable code:

~~~text
python -m msal.cli --input path/to/data.bin --output out/another-review
~~~

Invalid frame content gives matching ERR metadata; disagreement gives a failed review. Malformed transport/build/IO/deadline failures give exit 2. The normal app never invokes the deliberately faulty specimens. [Usage/help](docs/usage.md) covers setup, formats, troubleshooting and privacy.

## Validation commands

Create a virtual environment, install the full hash-locked development graph, then:

~~~text
python -m pip install --require-hashes -r requirements-dev.lock
python scripts/build.py
cargo fmt -- --check
cargo clippy --locked --all-targets -- -D warnings
cargo test --locked
cargo test --release --locked
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest --cov=msal --cov-report=term-missing:skip-covered
python scripts/code_map.py --check
python scripts/file_guide.py --check
python scripts/validate_repo.py
python scripts/benchmark.py
~~~

Linux CI separately installs official distro Clang/LLVM 18, validates C++ formatting and runs:

~~~text
python scripts/sanitizers.py --run-trusted-specimens
python scripts/fuzz.py
~~~

Do not run faulty specimens as production code or on shared/sensitive hosts. The harness permits only the authored examples; it is not a security sandbox for untrusted code. Sanitizer tools are not production-runtime protections.

## Documentation and evidence

Read [architecture](docs/architecture.md), [contracts](docs/contracts.md), [CWE/root-cause and fix guide](docs/defects.md), [testing strategy](docs/testing.md), [security boundaries](docs/security.md), [performance](docs/performance.md), [research](docs/research.md), and [validation report](docs/reports/validation.md).

All code files have purpose/function/class comments plus CI-checked exact-line symbol/variable indexes. Python indexes use AST; C++/Rust/CMake/workflow indexes are lexical occurrences, not claimed as semantic AST analysis. Native compilers and tests independently check syntax/behavior. Generated captures/diagnostics/builds remain ignored and local.

Current CI disables artifact/database uploads and Actions caching, including CodeQL's internal extraction and dependency caches. Early verification runs created three internal CodeQL caches; they are reported in validation evidence and retained pending fresh cleanup approval. Python and safe C++ security-extended CodeQL are separate from deliberate defect demonstrations; no alerts in repaired code are suppressed. GCC/Clang/MSVC and distro tool patch versions are logged; only Rust, development dependencies, scanner releases and action commits are pinned.

## Complete file guide

Generated from every tracked file; stale summaries or unknown purposes fail validation.

<!-- BEGIN FILE GUIDE -->

| File | Purpose |
| --- | --- |
| [.clang-format](.clang-format) | Jason Stys: readable deterministic C++ formatting, separate generated declaration indexes. |
| [.gitattributes](.gitattributes) | Consistent LF text checkouts across operating systems. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Jason Stys: cross-platform safe builds, real sanitizers/fuzzing and locked security gates, artifact/cache free. |
| [.github/workflows/codeql.yml](.github/workflows/codeql.yml) | Jason Stys: security-extended Python and safe C++ analysis; faulty specimens are not built in this job. |
| [.gitignore](.gitignore) | Exclude private diagnostics, builds, environments and generated fuzz artifacts. |
| [CMakeLists.txt](CMakeLists.txt) | Jason Stys: default safe C++20 build; deliberately faulty specimens are never targets here. |
| [Cargo.lock](Cargo.lock) | Complete dependency-free native Rust package graph. |
| [Cargo.toml](Cargo.toml) | Jason Stys: dependency-free safe Rust equivalents; no unsafe code or external crates. |
| [LICENSE](LICENSE) | MIT license for Jason Stys's authored code. |
| [README.md](README.md) | Memory Safety Analysis Lab. |
| [compile-fail/borrowed.rs](compile-fail/borrowed.rs) | Jason Stys: expected E0502 exercise; rustc must reject mutation during a live shared borrow. The shared view is used after attempted mutation, preserving the compile-time lifetime conflict. |
| [compile-fail/moved.rs](compile-fail/moved.rs) | Jason Stys: expected E0382 exercise; rustc must reject use after moving ownership. No executable is produced or run; the earlier move consumes the owned value. |
| [docs/architecture.md](docs/architecture.md) | ADR-001: separate safe analysis from deliberate fault specimens. |
| [docs/contracts.md](docs/contracts.md) | Data, ownership and process contracts. |
| [docs/defects.md](docs/defects.md) | Defect-to-fix teaching guide. |
| [docs/performance.md](docs/performance.md) | Complexity and performance methodology. |
| [docs/release.md](docs/release.md) | Source-release and maintenance checklist. |
| [docs/reports/benchmark.json](docs/reports/benchmark.json) | Measured release C++/Rust pipeline timing; no universal speed claim. |
| [docs/reports/ci.json](docs/reports/ci.json) | Immutable accepted-source CI snapshot, not a future guarantee. |
| [docs/reports/portfolio-sync-2026-10-22.md](docs/reports/portfolio-sync-2026-10-22.md) | <!-- File: docs/reports/portfolio-sync-2026-10-22.md; Purpose: certificate-bundle security repair and evidence by Jason Stys. -->. |
| [docs/reports/sanitizers.json](docs/reports/sanitizers.json) | Actual normalized hosted sanitizer and Rust compile-rejection evidence. |
| [docs/reports/validation.md](docs/reports/validation.md) | Validation and accepted-source evidence. |
| [docs/research.md](docs/research.md) | Primary research and implementation choices. |
| [docs/security.md](docs/security.md) | Security model and reporting policy. |
| [docs/testing.md](docs/testing.md) | Testing strategy and acceptance gates. |
| [docs/usage.md](docs/usage.md) | Setup, demos and troubleshooting. |
| [msal/\_\_init\_\_.py](msal/__init__.py) | Jason Stys: safe C++/Rust differential analysis and synthetic regression evidence. |
| [msal/cli.py](msal/cli.py) | Jason Stys: synthetic differential demo or bounded local-data review with inert no-overwrite reports. |
| [msal/core.py](msal/core.py) | Jason Stys: independent MSL1 reference decoder, deterministic corpus and strict native-result contract. |
| [msal/runner.py](msal/runner.py) | Jason Stys: deadline-bounded trusted native subprocesses and three-way differential evidence. |
| [native/fuzz.cpp](native/fuzz.cpp) | Jason Stys: libFuzzer callback exercises only safe bounded parser code under ASan/UBSan. |
| [native/main.cpp](native/main.cpp) | Jason Stys: bounded binary batch stdin worker; safe parser metadata only, no arbitrary file execution. |
| [native/safe.cpp](native/safe.cpp) | Jason Stys: safe C++20 parsing/ownership fixes for bounds, length arithmetic and stale lifetimes. |
| [native/safe.hpp](native/safe.hpp) | Jason Stys: bounds-checked owned record parsing and generation-safe handles; no raw owning pointers. |
| [native/tests.cpp](native/tests.cpp) | Jason Stys: always-active C++ bounds, ownership, stale-handle and malformed parser regressions. |
| [pyproject.toml](pyproject.toml) | Jason Stys: strict Python tooling and all-runtime-module branch/statement coverage. |
| [requirements-dev.in](requirements-dev.in) | Jason Stys: exact development-only tools; Python runtime uses only the standard library. |
| [requirements-dev.lock](requirements-dev.lock) | Universal full hash-locked Python development graph. |
| [rust-toolchain.toml](rust-toolchain.toml) | Jason Stys: fixed tested compiler, rustfmt and clippy rather than floating stable. |
| [rust/lib.rs](rust/lib.rs) | Jason Stys: safe Rust parser, checked length arithmetic and generation-safe owned handles. |
| [rust/main.rs](rust/main.rs) | Jason Stys: bounded binary batch worker emitting only safe Rust parser metadata. |
| [rust/tests.rs](rust/tests.rs) | Jason Stys: native Rust parser/ownership/bounds invariants and deterministic mutation exercise. |
| [scripts/benchmark.py](scripts/benchmark.py) | Jason Stys: repeated release C++/Rust process-inclusive performance comparisons on identical data. |
| [scripts/build.py](scripts/build.py) | Jason Stys: explicit default-safe CMake and Rust release builds; no specimen targets or global installs. |
| [scripts/code\_map.py](scripts/code_map.py) | Jason Stys: generate exact definition/variable line maps and verify Python function/class contracts. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Jason Stys: exact tracked-file README purpose inventory, unknown files fail rather than receive guesses. |
| [scripts/fuzz.py](scripts/fuzz.py) | Jason Stys: actual coverage-guided libFuzzer campaign on safe C++ parser, never faulty specimens. |
| [scripts/sanitizers.py](scripts/sanitizers.py) | Jason Stys: explicit trusted Linux specimen assertions, safe runtime sanitizer checks and coverage. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/validate\_repo.py](scripts/validate_repo.py) | Jason Stys: safe default-build isolation, private-state exclusion, action pins and exact local links. |
| [specimens/faults.cpp](specimens/faults.cpp) | Jason Stys: intentionally faulty synthetic sanitizer specimens; NEVER part of the default safe build. Execute only through the explicit Linux CI teaching harness; no arbitrary targets or exploit payloads. |
| [tests/test\_cli.py](tests/test_cli.py) | Jason Stys: actual worker/CLI privacy, no-overwrite output and process/batch failure regressions. |
| [tests/test\_core.py](tests/test_core.py) | Jason Stys: reference/native protocol bounds, deterministic corpus and malformed-data properties. |
| [tools.lock.json](tools.lock.json) | Official Linux scanner versions, URLs and SHA256 digests. |

<!-- END FILE GUIDE -->

MIT licensed. Passing bounded examples and campaigns are evidence for these inputs, not certification or proof that all possible programs/inputs are safe.
