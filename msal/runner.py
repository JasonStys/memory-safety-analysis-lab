"""Jason Stys: deadline-bounded trusted native subprocesses and three-way differential evidence."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 39
# definition: executable — line 42
# parameter: language — line 42
# definition: run — line 59
# parameter: inputs — line 59
# parameter: language — line 59
# parameter: timeout — line 59
# variable: path — line 67
# variable: completed — line 70
# definition: compare — line 82
# parameter: cases — line 82
# variable: _ — line 84
# variable: data — line 84
# variable: value — line 84
# variable: expected — line 85
# variable: value — line 85
# variable: cpp — line 86
# variable: rust — line 86
# variable: rows — line 87
# variable: _ — line 95
# variable: left — line 95
# variable: name — line 95
# variable: right — line 95
# variable: wanted — line 95
# variable: row — line 104
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


def run(language: str, inputs: list[bytes], timeout: float = 15) -> list[Outcome]:
    """Run fixed trusted worker with binary data stdin, no shell, ≤15s and bounded output schema."""
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 0.001 <= timeout <= 15
    ):
        raise ValueError("worker deadline outside contract")
    path = executable(language)
    if not path.is_file():
        raise ValueError("build safe C++ and Rust workers first")
    completed = subprocess.run(
        [str(path)],
        input=batch(inputs),
        capture_output=True,
        timeout=timeout,
        check=False,
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
