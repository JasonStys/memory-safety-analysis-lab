"""Jason Stys: deadline-bounded trusted native subprocesses and three-way differential evidence."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 40
# definition: executable — line 43
# parameter: language — line 43
# definition: run — line 64
# parameter: inputs — line 64
# parameter: language — line 64
# parameter: timeout — line 64
# variable: path — line 72
# variable: completed — line 79
# definition: compare — line 91
# parameter: cases — line 91
# variable: _ — line 93
# variable: data — line 93
# variable: value — line 93
# variable: expected — line 94
# variable: value — line 94
# variable: cpp — line 95
# variable: rust — line 95
# variable: rows — line 96
# variable: _ — line 104
# variable: left — line 104
# variable: name — line 104
# variable: right — line 104
# variable: wanted — line 104
# variable: row — line 113
# END CODE MAP

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from msal.core import Outcome, batch, outcomes, reference

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def executable(language: str) -> Path:
    """Resolve only this repository's safe builds, never arbitrary user-selected executables."""
    if getattr(sys, "frozen", False):
        if language not in ("cpp", "rust"):
            raise ValueError("unknown worker")
        return ROOT / "runtime" / ("parser-" + language + ".exe")
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
    if getattr(sys, "frozen", False):
        from .native_worker import run_owned

        return outcomes(run_owned(path, batch(inputs), timeout), len(inputs))
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
