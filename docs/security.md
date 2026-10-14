# Security model and reporting policy

Author: Jason Stys. Intended use: authorized developer, trusted repo-built tools, synthetic data.

Protect workstation integrity, private input, diagnostic paths/addresses and source credentials. Treat input bytes as untrusted data, not instructions. Native byte/record/batch caps, explicit bounds, typed error results, RAII/ownership and a Python job deadline constrain parser risk. Rust forbids unsafe blocks. C++ requires dynamic/static regression evidence; language choice alone is not a proof.

Default CMake/Cargo graphs exclude faulty specimens and compile-fail exercises; CLI workers cannot select arbitrary binaries, compile input or run a shell. Synthetic faulty children are trusted authored code, executed only by an explicit Linux opt-in harness on disposable CI. Separate processes are **not a security boundary for arbitrary hostile code**. No network target, telemetry, privileges, sandbox weakening or Docker changes are required.

Inert HTML escapes every report value; CSP default-src none, base-uri none, form-action none denies scripts, frames, resources and submission. No hosted website/login service or browser extension exists. Metadata/hashes can still be sensitive; keep output private. POSIX owner-only modes do not encrypt data or prevent administrator access; Windows NTFS inheritance must be reviewed for sensitive use.

Full-SHA Actions, no persisted checkout credentials, locked development hashes, official hash-verified scanner binaries, disabled artifact/database uploads and explicit CodeQL extraction/dependency-cache disabling reduce CI exposure. Early verification caches remain pending fresh deletion approval. Deliberate defects are public educational examples, not real secrets or vulnerabilities in another system. Raw runtime diagnostics stay in ignored out/; normalized actual evidence can be reviewed for publication.

Do not post credentials, customer code/data, local memory addresses or private paths in public issues. Share a minimal synthetic reproducer, version and stable error code through [GitHub](https://github.com/JasonStys) or contact [Jason Stys on LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/). No staffed support SLA, compliance certification or universal-safety guarantee is promised.
