# ADR-001: separate safe analysis from deliberate fault specimens

Status: accepted. Date: 2026-10-14. Author/maintainer: Jason Stys.

## Context and decision

Demonstrate memory reasoning and practical DevSecOps assurance without building an exploit tool or executing arbitrary submitted projects. Use a default-safe C++20/Rust decoder, an independent Python reference and deterministic synthetic data. Isolate tiny deliberately faulty C++ examples in specimens/, and Rust compile-fail exercises outside the Cargo crate.

| Component | Responsibility | Authority |
| --- | --- | --- |
| native/ | C++ owned parsing, arithmetic and generation handles | Default safe build; bounded stdin data |
| rust/ | Rust equivalents, no unsafe blocks | Default safe build; bounded stdin data |
| msal/ | Reference decoding, differential checks, private reports | Fixed built workers only, no shell/user code |
| specimens/ | Six intentional sanitizer triggers | Explicit opt-in Linux harness, separate binaries |
| compile-fail/ | Ownership/borrow rejection examples | rustc diagnostic assertions; never executed |
| scripts/ | Reproducible builds, assurance, benchmarks and metadata gates | Installed trusted tools, bounded jobs |

## Alternatives and trade-offs

Raw pointers and implicit ownership make lifetime errors harder to audit. C++ RAII/vector/string plus validated spans retain efficient native interfaces without manual frees. Rust documents what ownership checking prevents at compilation, while still requiring explicit logical/protocol bounds. Generation handles demonstrate logical stale-reference detection; they are not cross-arena authentication or thread-safe capabilities.

A full arbitrary-code analysis service would need strong OS/container isolation, sandbox escape defenses, dependency provenance, user authentication and private storage. This lab deliberately does not implement it. Separate subprocesses and disposable CI runners reduce interference but are **not a sandbox**.

Faulty examples never enter CMake's target graph or Cargo's source graph. CodeQL manually builds only safe C++ targets; intentional known-defect files are exercised in the sanitizer job instead. This is explicit analysis scope, not suppressing alerts in repaired code. Default app checks fixed trusted executables and sends bytes through stdin, never a source command or user-selected binary.

## Consequences and extension rules

New defect classes require a minimal synthetic specimen, exact diagnostic assertion, documented root cause/fix and repaired regression. New binary fields require matching contracts, independent reference cases and fuzz seeds. Keep variable/file maps current after formatting. Preserve raw generated diagnostics privately; publish normalized actual evidence only. Do not claim proof from agreement: multiple implementations may share a misunderstood specification.
