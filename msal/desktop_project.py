"""Graphical data-only differential/corpus review with the original C++/Rust/Python engines. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 94
# variable: PRODUCT — line 95
# variable: PROFILE — line 95
# variable: TITLE — line 96
# variable: VERSION — line 96
# variable: COLUMNS — line 97
# variable: RESOURCES — line 103
# variable: RESOURCE_LIMITS — line 110
# variable: MODES — line 111
# variable: REVIEW_MODE — line 116
# variable: CHOICES — line 117
# variable: FIELDS — line 130
# variable: ACTIVE_FIELDS — line 136
# variable: SCENARIOS — line 141
# variable: HELP — line 152
# definition: scenario — line 157
# parameter: name — line 157
# variable: index — line 161
# definition: prepared — line 171
# parameter: name — line 171
# variable: valid — line 173
# variable: choices — line 176
# definition: analyze — line 191
# parameter: parameters — line 192
# parameter: stage — line 192
# parameter: state — line 192
# variable: mode — line 196
# variable: cases — line 200
# variable: result — line 201
# variable: data — line 203
# variable: name — line 203
# variable: files — line 205
# variable: reduction — line 209
# variable: submitted — line 209
# variable: unique — line 209
# variable: raw_attempts — line 215
# variable: reduction — line 222
# variable: paths — line 226
# variable: value — line 228
# variable: raw — line 234
# variable: total — line 235
# variable: path — line 236
# variable: data — line 237
# variable: total — line 238
# variable: raw — line 243
# variable: data — line 244
# variable: copies — line 246
# variable: paths — line 248
# variable: data — line 249
# variable: index — line 249
# variable: path — line 250
# variable: output — line 253
# variable: result — line 254
# variable: files — line 257
# variable: path — line 258
# variable: submitted — line 260
# variable: unique — line 260
# variable: notes — line 261
# variable: disagreements — line 270
# variable: row — line 270
# definition: views — line 278
# parameter: files — line 278
# variable: report — line 280
# variable: row — line 284
# variable: row — line 286
# variable: row — line 289
# definition: cells — line 297
# parameter: row — line 297
# variable: cpp — line 300
# variable: rust — line 300
# variable: wanted — line 300
# variable: case — line 301
# definition: outcome_label — line 316
# parameter: outcome — line 316
# END CODE MAP

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, cast

from . import corpus as corpus_review
from .cli import render
from .core import MAX_BYTES, corpus, packet
from .desktop_io import Rejected, canonical, json_value
from .desktop_state import Workspace
from .inputs import read_source
from .runner import compare

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = "memory-safety-analysis-lab", "MemorySafetyAnalysisLab"
TITLE, VERSION = "Memory Safety Analysis Workbench", "1.1.0"
COLUMNS = (
    "Case / evidence",
    "Python: records / bytes",
    "C++ | Rust: records / bytes",
    "Agreement / scope",
)
RESOURCES = (
    "runtime/parser-cpp.exe",
    "runtime/parser-rust.exe",
    "notices.txt",
    "app.ico",
    "python314.dll",
)
RESOURCE_LIMITS: dict[str, int] = {}
MODES = (
    "Run original built-in differential corpus",
    "Review authorized data files",
    "Review prepared data exercise",
)
REVIEW_MODE = None
CHOICES = {
    "reduction": ("Do not reduce", "Reduce existing disagreements only"),
    "data_case": (
        "engineering-frame",
        "truncated-record",
        "unknown-tag",
        "maximum-records",
        "invalid-text",
        "trailing-bytes",
        "empty-header",
        "duplicates",
    ),
}
FIELDS = (
    ("inputs", "Authorized MSL1 data files (never source/programs)", "files"),
    ("data_case", "Prepared inert binary-data exercise", "choice"),
    ("reduction", "Optional original bounded disagreement reducer", "choice"),
    ("max_attempts", "Shared reduction attempts, 1–128", "text"),
)
ACTIVE_FIELDS = {
    MODES[0]: (),
    MODES[1]: ("inputs", "reduction", "max_attempts"),
    MODES[2]: ("data_case", "reduction", "max_attempts"),
}
SCENARIOS = (
    "Original 243-case independent differential corpus",
    "Valid bounded engineering sample",
    "Truncated record requires a safe parser error",
    "Unknown record tag remains rejected",
    "Maximum 128-record frame",
    "Non-ASCII text remains rejected",
    "Trailing bytes remain rejected",
    "Empty input is a header error",
    "Duplicate corpus and explicit reduction setting",
)
HELP = """Review data only with this project's actual fixed safe C++ and Rust parser executables and independent Python reference. Select authorized MSL1 data files, or choose an inert prepared example. No uploaded source, arbitrary compiler/executable, plugin, intentionally faulty specimen, live target or network is accepted. Valid frames and consistent parser rejections both count as agreement; disagreement remains a failed comparison, and process/IO/timeout failure remains an error.
The built-in operation preserves the original 243 named corpus cases. Private-file and prepared-data review use the original content-hash deduplication and optional shared-budget reducer. Reduction runs only if a disagreement already exists, requires the same agreement partition twice, and retains hashes/lengths rather than payloads. A local chunk minimum is not global minimality or proof of a common root cause; exhausted/unattempted reductions remain inconclusive. Files are at most 1 MiB each, 1000 submitted and 8 MiB aggregate including frame headers. The fixed native workers retain their original 15-second deadline.
Inspect independent expected/C++/Rust metadata, input hashes and reduction evidence. Search never changes denominators or exports. Keep private originals separately: saved/exported reports contain no raw payload bytes. History is owner-local plaintext, not encrypted or multiuser authentication. Exit retains the worker/owner lock until evidence is committed and owned children have completed. Agreement is not universal memory safety; source CI's actual sanitizers, faulty-specimen controls, coverage and fuzzers remain separate mandatory checks."""


def scenario(name: str) -> dict[str, str]:
    """Populate ordinary editable controls; prepared selection never executes an analysis."""
    if name not in SCENARIOS:
        raise Rejected("unknown prepared data exercise")
    index = SCENARIOS.index(name)
    return {
        "mode": MODES[0] if index == 0 else MODES[2],
        "inputs": "",
        "data_case": CHOICES["data_case"][max(0, index - 1)],
        "reduction": CHOICES["reduction"][int(index == 8)],
        "max_attempts": "32",
    }


def prepared(name: str) -> list[bytes]:
    """Return inert supported binary examples; malformed content exercises safe parser errors, never unsafe code."""
    valid = packet(
        [(1, b"\x2a\x00\x00\x00"), (2, b"pressure-sensor-A"), (3, b"\x00\xff")]
    )
    choices = {
        "engineering-frame": [valid],
        "truncated-record": [valid[:-1]],
        "unknown-tag": [b"MSL1\x01\x00\x04\x00\x00"],
        "maximum-records": [packet([(3, b"x" * 256)] * 128)],
        "invalid-text": [b"MSL1\x01\x00\x02\x01\x00\xff"],
        "trailing-bytes": [packet([]) + b"extra"],
        "empty-header": [b""],
        "duplicates": [valid, valid, valid[:-1]],
    }
    if name not in choices:
        raise Rejected("unknown prepared binary case")
    return choices[name]


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Reuse the original three-way comparison and corpus/reduction engines; never compile or execute submitted data."""
    del state
    mode = parameters.get("mode", "")
    if mode not in MODES:
        raise Rejected("unsupported data review")
    if mode == MODES[0]:
        cases = corpus()
        result = cast(dict[str, Any], compare(cases))
        result["input_sha256"] = {
            name: hashlib.sha256(data).hexdigest() for name, data in cases
        }
        files = {
            "report.json": canonical(result),
            "report.html": render(result).encode(),
        }
        submitted, unique, reduction = (
            len(cases),
            len(cases),
            "not requested in original corpus operation",
        )
    else:
        raw_attempts = parameters.get("max_attempts", "").strip()
        if (
            not raw_attempts.isascii()
            or not raw_attempts.isdecimal()
            or not 1 <= int(raw_attempts) <= 128
        ):
            raise Rejected("reduction attempts must be 1 to 128")
        reduction = parameters.get("reduction", "")
        if reduction not in CHOICES["reduction"]:
            raise Rejected("explicit reduction setting required")
        if mode == MODES[1]:
            paths = [
                Path(value)
                for value in parameters.get("inputs", "").splitlines()
                if value.strip()
            ]
            if not 1 <= len(paths) <= 1000:
                raise Rejected("select 1 to 1000 explicit data files")
            # Read stable bounded descriptors first, then feed the ORIGINAL corpus engine owned exact copies.
            raw = []
            total = 0
            for path in paths:
                data = read_source(path, MAX_BYTES)
                total += len(data) + 4
                if total > 8 * MAX_BYTES:
                    raise Rejected("submitted corpus exceeds 8 MiB")
                raw.append(data)
        else:
            raw = prepared(parameters.get("data_case", ""))
        if sum(len(data) + 4 for data in raw) > 8 * MAX_BYTES:
            raise Rejected("submitted corpus exceeds 8 MiB")
        copies = stage / "private-inputs"
        copies.mkdir()
        paths = []
        for index, data in enumerate(raw):
            path = copies / f"frame-{index:04}.bin"
            path.write_bytes(data)
            paths.append(path)
        output = stage / "corpus-result"
        result = corpus_review.review(
            paths, output, reduction == CHOICES["reduction"][1], int(raw_attempts)
        )
        files = {
            path.name: read_source(path, 32 * 1024 * 1024) for path in output.iterdir()
        }
        submitted, unique = result["submitted_files"], result["case_count"]
    notes = {
        "schema": 1,
        "origin": mode,
        "submitted_cases": submitted,
        "evaluated_cases": unique,
        "reduction": reduction,
        "scope": "Actual fixed safe parsers and independent Python oracle. Inputs remain private data; no arbitrary code, faulty specimens, sanitizers or fuzzers execute in this application. Agreement does not prove universal memory safety.",
    }
    files["input-scope.json"] = canonical(notes)
    disagreements = sum(not row["matches"] for row in result["cases"])
    return (
        "safe-parser-review",
        f"{unique} three-way cases; {disagreements} disagreements; {submitted - unique} duplicate inputs; no arbitrary code",
        files,
    )


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Expose complete original metadata and explicit scope, without replacing a parser failure by a finding."""
    report = json_value(
        files["report.json"] if "report.json" in files else files["corpus.json"]
    )
    return {
        "Three-way case outcomes": [{"kind": "case", **row} for row in report["cases"]],
        "Disagreements only": [
            {"kind": "case", **row} for row in report["cases"] if not row["matches"]
        ],
        "Reduction observations": [
            {"kind": "reduction", **row} for row in report.get("reductions", [])
        ],
        "Unfiltered scope and denominator": [
            {"kind": "scope", **json_value(files["input-scope.json"])}
        ],
    }


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Summarize literal outcomes legibly; full hashes/fingerprints stay available in selected JSON detail."""
    if row.get("kind") == "case":
        wanted, cpp, rust = row["expected"], row["cpp"], row["rust"]
        case = str(row["case"])
        return (
            case[:16] + "…" if len(case) == 64 else case,
            outcome_label(wanted),
            outcome_label(cpp) + " | " + outcome_label(rust),
            "AGREEMENT" if row["matches"] else "DISAGREEMENT",
        )
    return (
        str(row.get("initial_sha256", row.get("kind", "evidence"))),
        str(row.get("state", row.get("submitted_cases", ""))),
        str(row.get("attempts", row.get("evaluated_cases", ""))),
        str(row.get("scope", "bounded original reducer")),
    )


def outcome_label(outcome: dict[str, Any]) -> str:
    """Keep record/byte counts or the actual parser-error code visible without serializing a dictionary into a cell."""
    if outcome["status"] == "ok":
        return f"OK {outcome['count']}r/{outcome['bytes']}B"
    return "ERR " + str(outcome["code"])
