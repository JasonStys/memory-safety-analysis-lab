# Installed Windows 1.1.0: validation and user guide

By Jason Stys. 11 November 2026.

The independently downloaded installed application uses exact clean runtime source `2526a32020cc7628e36e8931ef3be65eee2a0d5c`. Historical reports and Office editions remain unchanged.

## Purpose and practical improvements

Compare a fixed binary-record parser in independently built C++, Rust and Python implementations. Inspect malformed inputs, exact result disagreements, corpus construction and bounded reduction without compiling or executing submitted source files.

The original lab retains safe cross-language parsers, differential checks, sanitizer/fuzzing evidence and repeatable malformed-input corpora. The new desktop workbench uses those real engines, supports bounded local data inputs, keeps immutable review history and exports complete evidence through normal GUI controls.

## Actual validation

**Independent distribution: Passed.** Downloaded provider assets, sidecar and installed file identities matched. The complete installed app was used; installation resources remained byte-identical.

**Actual app use and restart: Passed.** Nine actual workflows and nine retained bundles passed the complete original installed consumer; two launches exited normally and the exact history/export bytes reopened.

**Source and security: Passed.** All current main workflows passed before publication. All configured exact-source processed CodeQL categories had zero raw findings and zero open alerts.

**Individual shortcut: Verified.** Desktop and Start-menu targets were read back against the installed version. Normal default-profile shortcut activation is separate from full installed executable acceptance.

## Illustrated operation and implementation

The [four-page application guide](windows-application-guide-1.1.0.docx) contains two actual installed screenshots, a practical user journey and immutable code. Its [review manifest](windows-application-guide-1.1.0.json) records exact document, image, code and page identities.

Download the matching version and checksum from Releases. This is an unsigned per-user portable Windows x64 app; keep its complete accompanying files together. No system Python installation or Docker change is needed.

Use the individual Desktop icon and in-app help. Inputs, saved evidence and exports stay outside the installation. Preserve older versions and your own profiles; tests used only separate synthetic inputs.

Passing a finite corpus does not prove the absence of memory bugs. The bundled parsers and reducer have a fixed protocol and bounds; the GUI does not compile or run arbitrary supplied source.

This owner-local evidence tool does not authenticate another reviewer or encrypt data against the same Windows account. Original sanitizer and broader fuzzing jobs are separate CI evidence.

Only synthetic prepared inputs and isolated retained profiles were used. Ordinary user accounts and local Docker were not opened or changed. Shortcut target read-back and full installed-executable tests are separate from ordinary default-profile icon activation. This documentation revision still requires its own original hosted gates and processed security analyses.
