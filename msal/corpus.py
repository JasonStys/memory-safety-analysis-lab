"""Jason Stys: content-addressed data-only corpus review and budgeted owned-worker disagreement reduction."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: minimize — line 75
# parameter: data — line 76
# parameter: max_attempts — line 76
# parameter: seconds — line 76
# variable: deadline — line 87
# variable: attempts — line 88
# definition: signature — line 90
# parameter: candidate — line 90
# variable: attempts — line 95
# variable: expected — line 96
# variable: cpp — line 97
# variable: remaining — line 100
# variable: rust — line 103
# variable: current — line 106
# variable: state — line 107
# variable: target — line 108
# variable: target — line 110
# variable: state — line 113
# variable: state — line 115
# variable: width — line 116
# variable: position — line 118
# variable: candidate — line 120
# variable: current — line 125
# variable: position — line 127
# variable: width — line 128
# variable: state — line 130
# definition: review — line 145
# parameter: inputs — line 146
# parameter: max_attempts — line 146
# parameter: output — line 146
# parameter: reduce — line 146
# variable: unique — line 153
# variable: total_bytes — line 154
# variable: path — line 155
# variable: p — line 158
# variable: data — line 161
# variable: total_bytes — line 162
# variable: cases — line 166
# variable: _ — line 167
# variable: data — line 167
# variable: result — line 168
# variable: reductions — line 171
# variable: deadline — line 173
# variable: remaining_attempts — line 174
# variable: row — line 175
# variable: remaining_seconds — line 177
# variable: _ — line 183
# variable: evidence — line 183
# variable: remaining_attempts — line 187
# variable: target — line 192
# variable: p — line 193
# definition: main — line 201
# variable: parser — line 203
# variable: args — line 210
# variable: result — line 212
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any, cast

from msal.cli import read, render, save
from msal.core import MAX_BYTES, batch, reference
from msal.runner import compare, run


def minimize(
    data: bytes, max_attempts: int = 32, seconds: int = 10
) -> tuple[bytes, dict[str, Any]]:
    """Deterministically delete chunks only while the same owned C++/Rust/reference disagreement persists twice."""
    if (
        len(data) > MAX_BYTES
        or type(max_attempts) is not int
        or not 1 <= max_attempts <= 128
        or type(seconds) is not int
        or not 1 <= seconds <= 30
    ):
        raise ValueError("reduction bounds")
    deadline = time.monotonic() + seconds
    attempts = 0

    def signature(candidate: bytes) -> tuple[bool, bool, bool]:
        """Require well-formed actual worker outcomes; process failure/timeouts never count as preserved disagreement."""
        nonlocal attempts
        if attempts >= max_attempts or deadline - time.monotonic() < 0.002:
            raise TimeoutError("reduction budget")
        attempts += 1
        expected = reference(candidate)
        cpp = run(
            "cpp", [candidate], timeout=min(15, (deadline - time.monotonic()) / 2)
        )[0]
        remaining = deadline - time.monotonic()
        if remaining < 0.001:
            raise TimeoutError("reduction budget")
        rust = run("rust", [candidate], timeout=min(15, remaining))[0]
        return cpp == expected, rust == expected, cpp == rust

    current = data
    state = "NO_DISAGREEMENT"
    target: tuple[bool, bool, bool] | None = None
    try:
        target = signature(current)
        if target != (True, True, True):
            if signature(current) != target:
                state = "UNSTABLE_ORACLE"
            else:
                state = "LOCAL_CHUNK_MINIMUM"
                width = max(1, len(current) // 2)
                while width:
                    position = 0
                    while position < len(current):
                        candidate = current[:position] + current[position + width :]
                        if (
                            signature(candidate) == target
                            and signature(candidate) == target
                        ):
                            current = candidate
                        else:
                            position += width
                    width //= 2
    except (TimeoutError, subprocess.TimeoutExpired):
        state = "BUDGET_EXHAUSTED"
    return current, {
        "state": state,
        "attempts": attempts,
        "attempt_cap": max_attempts,
        "seconds_cap": seconds,
        "initial_bytes": len(data),
        "retained_bytes": len(current),
        "initial_sha256": hashlib.sha256(data).hexdigest(),
        "retained_sha256": hashlib.sha256(current).hexdigest(),
        "agreement_signature": target,
        "scope": "Owned safe parser workers only. Twice-confirmed equality/disagreement partition, not root-cause equivalence or proof of global minimality. Worker failures propagate; timeouts are inconclusive. No arbitrary program is accepted.",
    }


def review(
    inputs: list[Path], output: Path, reduce: bool = False, max_attempts: int = 32
) -> dict[str, Any]:
    """Deduplicate bounded explicit ordinary data files by hash; never import executable/source plugins or erase a corpus."""
    if type(max_attempts) is not int or not 1 <= max_attempts <= 128:
        raise ValueError("reduction attempts")
    if not 1 <= len(inputs) <= 1000:
        raise ValueError("corpus count")
    unique: dict[str, bytes] = {}
    total_bytes = 0
    for path in inputs:
        if any(
            p.is_symlink() or p.is_junction()
            for p in (path.absolute(), *path.absolute().parents)
        ):
            raise ValueError("linked data input")
        data = read(path)
        total_bytes += len(data) + 4
        if total_bytes > 8 * MAX_BYTES:
            raise ValueError("submitted corpus byte cap")
        unique.setdefault(hashlib.sha256(data).hexdigest(), data)
    cases = sorted(unique.items())
    batch([data for _, data in cases])
    result = compare(cases)
    result["submitted_files"] = len(inputs)
    result["duplicate_files"] = len(inputs) - len(cases)
    reductions: list[dict[str, Any]] = []
    if reduce:
        deadline = time.monotonic() + 30
        remaining_attempts = max_attempts
        for row in cast(list[dict[str, Any]], result["cases"]):
            if not row["matches"]:
                remaining_seconds = min(10, int(deadline - time.monotonic()))
                if remaining_seconds < 1 or remaining_attempts < 1:
                    reductions.append(
                        {"state": "NOT_ATTEMPTED_BUDGET", "initial_sha256": row["case"]}
                    )
                    continue
                _, evidence = minimize(
                    unique[row["case"]], remaining_attempts, remaining_seconds
                )
                reductions.append(evidence)
                remaining_attempts -= evidence["attempts"]
    result["reductions"] = reductions
    result["payload_retention"] = (
        "Reports contain metadata only; rerun deterministic reduction against private original corpus to reproduce hashes. No reduced bytes or source paths are exported."
    )
    target = output.absolute()
    if any(p.is_symlink() or p.is_junction() for p in (target, *target.parents)):
        raise ValueError("linked corpus output")
    target.mkdir(mode=0o700)
    save(target / "corpus.json", json.dumps(result, sort_keys=True, indent=2).encode())
    save(target / "corpus.html", render(result).encode())
    return result


def main() -> int:
    """Review explicit data files and optionally diagnose existing disagreements; never save payloads or source paths in reports."""
    parser = argparse.ArgumentParser(
        description="Jason Stys — data-only owned-parser corpus review"
    )
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimize", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=32)
    args = parser.parse_args()
    try:
        result = review(args.input, args.output, args.minimize, args.max_attempts)
        print(
            json.dumps(
                {
                    "unique_cases": result["case_count"],
                    "duplicates": result["duplicate_files"],
                    "passed": result["passed"],
                }
            )
        )
        return 0 if result["passed"] else 1
    except (ValueError, OSError, subprocess.TimeoutExpired):
        print(
            "Corpus review rejected; check owned builds, bounded data and new output directory."
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
