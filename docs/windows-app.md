# Windows application: memory-safety-analysis-lab

Created by Jason Stys: [GitHub](https://github.com/JasonStys) · [LinkedIn/contact](https://www.linkedin.com/in/jason-stys-31b30b351/).

## Launch and use

Open **MemorySafetyAnalysisLab.exe** from an admitted portable distribution. It contains the runtime and opens its own real Tk application window. Help and runtime licenses are available inside the app. No browser, account, password, Python, compiler or manual setup is required for end users. Source developers can run `python -m msal.desktop` after following the original project's setup; native-only bundled dependencies are built by the recipe below.

Choose the original 243-case corpus, select multiple authorized MSL1 binary data files, or populate an editable prepared exercise. Run the original safe C++ and Rust workers against the independent Python reference. Valid data and consistent parser errors are both meaningful outcomes; a disagreement remains a failed comparison and a process failure is an error. Inspect exact metadata, hashes, duplicate counts and reduction scope, then export the saved evidence without raw payloads. Optional reduction uses the existing shared attempt/deadline budget and only starts when a disagreement already exists.

1. Select a mode and authorized supported inputs. Prepared cases populate normal editable controls; selecting a case does not run it.
2. Review parameters and run. A retained worker invokes the actual existing project engine; controls prevent overlapping operations.
3. Select the saved run, inspect summary/detail and filter findings. Filters do not change original evidence or denominators.
4. Export the complete selected bundle into a **new** chosen directory. Existing files are not overwritten. Delete history only after explicit confirmation.
5. Use Exit or the window close button. During work, the window and profile lock remain until the worker and owned children finish. No force-close success is claimed.

## Private local storage

The default Windows profile is under the current OS user's local application-data directory, outside the repository, executable and installation directories. One process owns its marker/lock/SQLite workspace. History is owner-local **plaintext**, not encrypted storage or multiuser authentication. Do not share sensitive profiles or use an untrusted OS account. Optional explicit source/developer profile paths must be ordinary owned directories outside the source/program root.

Fixed database, marker, lock and SQLite sidecars are admitted before initialization: symlinks, junctions, hardlinks and directory substitutions are refused. Ordinary recovery sidecars remain admitted; no database reset or sidecar deletion is used as recovery. Saved bundles have fixed size/count limits and retain exact hashes. Import failures leave the last saved history unchanged. Read-only source inputs stay untouched. Same-OS administrator attacks and arbitrary concurrent directory mutation are outside this static ownership boundary.

## Scope and troubleshooting

The GUI does not accept source code, executable/compiler paths, plugins, unsafe specimens or network targets. It never claims that agreement proves universal memory safety. Sanitizers, compile-rejection controls, C++ coverage, libFuzzer and Rust mutation tests remain separate original CI gates. The shipped two fixed safe workers are the actual compiled engines; no Python replacement is used in frozen review.

An invalid/oversized input, inconsistent report, stale state or failed child is shown as an error, never a successful empty analysis. Keep originals; exports are reports, not a backup of all source inputs. Close an existing instance before reusing a profile. If startup refuses a linked/unrecognized profile, choose a separate ordinary owned path; do not delete recovery files or reset private data to suppress the error.

## Build and test the actual portable file

Use an isolated Windows CPython **3.14.10** SDK with Tcl/Tk and the repository's exact hash-locked dependencies:

```text
python -m pip install --require-hashes -r requirements-dev.lock -r requirements-native.lock
python -m pip check
python scripts/build_native.py
python scripts/test_native_app.py
```

The builder records actual source/dirty state and resource digests; CI requires a clean checkout. The independent consumer opens the compiled executable, drives the same widgets/handlers/mainloop, checks real project results, exports, errors, minimum window layout, help/licenses and two-process durable reopen. It does not install the app, create shortcuts, touch normal profiles or publish a release. A clean source digest/checksum establishes byte identity, not publisher identity, legal clearance or absence of every defect.
