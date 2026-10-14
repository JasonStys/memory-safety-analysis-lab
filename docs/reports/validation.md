# Validation report

Author: Jason Stys. Local safe-build checks pass; hosted sanitizer/fuzz/coverage and final CI evidence will be recorded before handoff.

Locally, existing MSVC compiled the C++ safe implementation and 179 always-active invariant assertions passed. Rust debug tests and clippy pass; 100,000 deterministic mutation cases are included in the native suite. All three native/reference implementations agree on the 243-case corpus. Python tests include real worker invocation, arbitrary-byte property cases and private-report checks; final measured coverage is recorded after CI acceptance.

No deliberately faulty executable was run on this PC. Hosted Linux will assert six expected sanitizer failures and two Rust compilation rejections, then require clean repaired runtime tests, measured line coverage and actual libFuzzer completion. These are pending, not advertised as successful until verified.

Default CI is artifact/cache free. Account-level storage/billing evidence stays local; no run deletion or setting change is authorized/performed. No private input, build output or raw diagnostics are tracked.
