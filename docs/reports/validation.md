# Validation and accepted-source evidence

Author: Jason Stys. Recorded 2026-10-14 14:56:19 UTC. Accepted implementation: 06c995974fe84e1802d8bf9e5e8ef243c5dea420. All nine hosted jobs pass. [Immutable CI snapshot](ci.json) records source, job links and timestamps; later documentation commits must independently pass before handoff.

## Actual tests and measurements

| Check | Actual result / scope |
| --- | --- |
| Local C++ Release | MSVC 19.44; 179 always-active invariant assertions, no NDEBUG suppression |
| Rust debug/release | Six tests per profile; 100,000 deterministic mutation cases per profile, zero failures |
| Python | 41 tests pass; four runtime modules, 99.16% combined statement/branch coverage, 95% gate |
| Three-way corpus | All 243 C++/Rust/Python expected/observed rows agree |
| Property test | 200 reproducible arbitrary-byte cases through actual workers |
| Sanitizer specimens | Six exact expected ASan/UBSan/LSan signals and nonzero exits matched |
| Rust compile-fail | Both exact ownership/borrow error codes matched; no executable run |
| Repaired C++ runtime | Unit suite/corpus/batch error checks clean under ASan/UBSan with leak checks |
| C++ source coverage | 99.3006993% line coverage of native/safe.cpp and native/main.cpp; not inferred branch coverage |
| Coverage-guided fuzz | Actual libFuzzer completion of 20,000 runs, seed 12345, no sanitizer crash |
| Native/static/security gates | Clang formatting, C++ warning-as-error, Rust fmt/clippy, Ruff/strict mypy, locked graph audit, Gitleaks, actionlint all pass |
| Matrix | Linux Python 3.12/3.14, Windows 3.14, macOS 3.14 all pass |
| CodeQL | Python and safe C++ security-extended jobs pass; zero open alerts at acceptance |

[Accepted Validate](https://github.com/JasonStys/memory-safety-analysis-lab/actions/runs/38584506068) and [accepted CodeQL](https://github.com/JasonStys/memory-safety-analysis-lab/actions/runs/38584506151) support the table. [Normalized actual sanitizer report](sanitizers.json) was extracted from the completed job's own output, not fabricated. Compiler: Ubuntu Clang 18.1.3. Raw private diagnostics, addresses, builds and profiles are not tracked.

The faulty children deliberately fail; it is the exact expected-diagnostic assertion that passes. An unrelated crash, missing sanitizer runtime or clean faulty exit would fail CI. No faulty executable was run on this PC. Hosted subprocesses are trusted examples, not an arbitrary-code sandbox.

[Windows benchmark snapshot](benchmark.json), recorded 2026-10-14T14:33:49.954433+00:00, contains seven raw timings after warmup for each 100-frame workload at 1/32/128 records and both Release implementations. Startup, framing, parsing/hash and Python output validation are included. CI reruns the correctness/timing exercise independently. No universal performance, peak-memory, fuzz-completeness or safety proof is claimed.

## Corrections and honest history

The [initial Windows job](https://github.com/JasonStys/memory-safety-analysis-lab/actions/runs/38582879252/job/115917089297) failed because the hosted machine did not have Visual Studio 2022. The build now preserves CMake's supported default/cached generator and platform. Both the current hosted Windows job and repeat local builds pass. That original failure remains visible; no history was deleted or mislabeled.

Local checks also caught an oversized pytest parameter label and an overly broad core-dump ignore pattern that would omit the Python reference module. Explicit case IDs and a tracked-runtime-module gate fixed these before acceptance. No test, sanitizer or alert was suppressed to create green output.

CodeQL automatically wrote three extraction caches in early verification despite no explicit cache action. Current workflows explicitly disable both TRAP/extraction and dependency caching; a repository gate checks the flags. At acceptance, artifact count is zero and three pre-existing caches total 45,568,175 bytes (~45.57 MB). No additional cache key appeared in the accepted run. Existing caches are retained pending fresh cleanup approval; no deletion or account billing/retention change occurred. Account-level storage evidence remains private/local.

## Limits and release readiness

Line coverage includes only the two authored C++ runtime source files; Python coverage includes every runtime module. Headers/test/fuzz harnesses and faulty specimens are not misrepresented as application coverage. Rust mutation testing is not coverage-guided Rust fuzzing. CodeQL safe C++ build scope intentionally excludes faulty specimens and does not suppress repaired-code findings.

The local app's reports include input SHA256 and metadata only, with escaped inert HTML and no payload/path exports. Output remains ignored and private; Windows ACLs and administrator access are documented. Final-main documentation checks, alerts and cache/artifact counts are rechecked before handoff. See [release checklist](../release.md), [contracts](../contracts.md), and [security model](../security.md).
