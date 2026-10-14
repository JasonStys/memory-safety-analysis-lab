"""Jason Stys: deadline-bounded trusted native subprocesses and three-way differential evidence."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 38
# definition: executable — line 41
# parameter: language — line 41
# definition: run — line 58
# parameter: inputs — line 58
# parameter: language — line 58
# variable: path — line 60
# variable: completed — line 63
# definition: compare — line 71
# parameter: cases — line 71
# variable: _ — line 73
# variable: data — line 73
# variable: value — line 73
# variable: expected — line 74
# variable: value — line 74
# variable: cpp — line 75
# variable: rust — line 75
# variable: rows — line 76
# variable: _ — line 84
# variable: left — line 84
# variable: name — line 84
# variable: right — line 84
# variable: wanted — line 84
# variable: row — line 93
# END CODE MAP

from __future__ import annotations

import os
import subprocess
from dataclasses import asdict
from pathlib import Path

from msal.core import Outcome, batch, outcomes, reference

ROOT = Path(__file__).resolve().parents[1]


def executable(language: str) -> Path:
    """Resolve only this repository's safe builds, never arbitrary user-selected executables."""
    if language == "cpp":
        return (
            ROOT
            / "out/cpp"
            / ("Release/parser-cpp.exe" if os.name == "nt" else "parser-cpp")
        )
    if language == "rust":
        return (
            ROOT
            / "target/release"
            / ("parser-rust.exe" if os.name == "nt" else "parser-rust")
        )
    raise ValueError("unknown worker")


def run(language: str, inputs: list[bytes]) -> list[Outcome]:
    """Run fixed trusted worker with binary data stdin, no shell, ≤15s and bounded output schema."""
    path = executable(language)
    if not path.is_file():
        raise ValueError("build safe C++ and Rust workers first")
    completed = subprocess.run(
        [str(path)], input=batch(inputs), capture_output=True, timeout=15, check=False
    )
    if completed.returncode:
        raise ValueError("native batch/worker failure")
    return outcomes(completed.stdout, len(inputs))


def compare(cases: list[tuple[str, bytes]]) -> dict[str, object]:
    """All three results must agree; mismatch evidence is retained rather than mislabeled successful."""
    data = [value for _, value in cases]
    expected = [reference(value) for value in data]
    cpp, rust = run("cpp", data), run("rust", data)
    rows = [
        {
            "case": name,
            "expected": asdict(wanted),
            "cpp": asdict(left),
            "rust": asdict(right),
            "matches": wanted == left == right,
        }
        for (name, _), wanted, left, right in zip(
            cases, expected, cpp, rust, strict=True
        )
    ]
    return {
        "schema": "msal-differential-v1",
        "author": "Jason Stys",
        "mode": "safe-data-only",
        "case_count": len(cases),
        "passed": all(row["matches"] for row in rows),
        "cases": rows,
    }
