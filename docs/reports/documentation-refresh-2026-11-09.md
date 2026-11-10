# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `dc68386d9cd6ec62a9ce9d02723f37bb43ad2935`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File | Bytes | SHA-256 | Reviewed scope |
| --- | ---: | --- | --- |
| [project-guide.docx](project-guide.docx) | 43878 | `56265b1ddf004f211add36f144e819c9d4dd10de91a6eb2ba211c200dd0f3b37` | 4 pages, each viewed individually |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval.

## Evidence and change boundary

- Functional baseline: `dc68386d9cd6ec62a9ce9d02723f37bb43ad2935`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Actual integration validation

59 Python tests passed with 98.45% combined runtime statement/branch coverage, retaining the 95% floor. Eight independent real-ZIP documentation-input regressions are included. Ruff/format, strict mypy, generated maps, exhaustive tracked-file inventory and original privacy/workflow contracts passed.

The existing tracked-source privacy guard now reads bounded XML and relationships from exact reviewed Office paths. Unknown binaries still fail strict UTF-8 handling. Each package is opened once and checked against descriptor/member/expansion budgets; encrypted, macro or embedded payloads are rejected and no Office content is executed. These documentation checks do not replace the original hosted native/compiler/security gates or the dated functional measurements in the Word edition.
