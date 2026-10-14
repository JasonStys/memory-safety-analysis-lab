# Setup, demos and troubleshooting

Created by Jason Stys. Contact via [GitHub](https://github.com/JasonStys) or [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/).

Install Python, CMake, rustup and your platform's C++20 development tools from official sources. Windows needs Visual Studio 2022 C++ tools; CMake configures that generator. Ensure cmake/ctest/cargo are on your development shell's PATH. The app requires no pip packages, driver or administrator access. PowerShell activation is optional; do not weaken execution policy/security settings.

Run python scripts/build.py from the repo root. It configures only safe C++ targets, builds/tests Release and builds the pinned Rust release. Then python -m msal.cli --output out/review compares the full generated corpus and creates report.json/report.html. Open report.html locally and use browser Find for case/error labels.

The optional --input is a local **MSL1 data file**. It is not arbitrary C++/Rust source, a project tree or executable; no user code is compiled. See [format/limits](contracts.md). Invalid data that all decoders reject consistently is a successful agreement review, not an accepted valid packet. A real discrepancy is marked failed and returns exit 1. IO/build/transport/deadline failure returns exit 2 without logging raw inputs.

For tests create a virtual environment, install requirements-dev.lock with --require-hashes, and run the README commands. Normal source/batch builds work on the supported matrix platforms. Linux-only optional teaching commands need distro Clang/LLVM 18 and sanitizer runtimes; scripts/sanitizers.py requires --run-trusted-specimens. Do not run specimens on shared/production machines. Docker remains unused.

Output directories must be new. The app will not overwrite old evidence. After a failed write, a partial new folder may remain; preserve it for diagnosis or remove it yourself and use a new path. Check input ≤1 MiB, safe native build paths, matching toolchain and writable private output directory when exit 2 occurs. Oversized batches fail before exposing partial results.

Reports are not encrypted. Use a private user-profile folder; verify Windows NTFS ACLs before sensitive use. Never commit real data/diagnostics. The default .gitignore excludes generated working state; repository privacy/secret gates add checks, not guaranteed detection of every sensitive value. For this portfolio only synthetic inputs are validated.
