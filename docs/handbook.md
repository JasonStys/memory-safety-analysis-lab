# Memory Safety Analysis Lab handbook

By Jason Stys.

Deduplicate private corpus inputs and reduce twice-confirmed owned-parser disagreements under shared time/attempt budgets.

Deduplicate private corpus inputs and reduce twice-confirmed owned-parser disagreements under shared time/attempt budgets.

Produces reproducible smaller debugging cases while preserving unstable and inconclusive outcomes.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |

The editable Markdown remains the maintenance source. The Word files are readable editions. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [release](release.md)
- [usage](usage.md)

### Design and contracts

- [architecture](architecture.md)
- [contracts](contracts.md)
- [research](research.md)

### Security and validation

- [performance](performance.md)
- [security](security.md)
- [testing](testing.md)

## Historical results and reproduction

The reviewed source is [`dc68386d9cd6ec62a9ce9d02723f37bb43ad2935`](https://github.com/JasonStys/memory-safety-analysis-lab/tree/dc68386d9cd6ec62a9ce9d02723f37bb43ad2935). The observed functional workflow baseline is `dc68386d9cd6ec62a9ce9d02723f37bb43ad2935`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/corpus-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/memory-safety-analysis-lab/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Reduction preserves a twice-confirmed agreement/disagreement partition, not necessarily the same root cause or a globally minimal input.
- Unstable and inconclusive executions remain distinct from reproducible findings under shared attempt/time budgets.
- Exported reduction reports contain hashes and lengths rather than source paths or payload bytes; the library can return bytes to its caller.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.


## Native desktop workbench

See [desktop controls and owner-local privacy](windows-app.md) and [dated actual native validation](reports/native-workbench-2026-11-11.md). The GUI does not accept source code, executable/compiler paths, plugins, unsafe specimens or network targets. It never claims that agreement proves universal memory safety. Sanitizers, compile-rejection controls, C++ coverage, libFuzzer and Rust mutation tests remain separate original CI gates. The shipped two fixed safe workers are the actual compiled engines; no Python replacement is used in frozen review.
