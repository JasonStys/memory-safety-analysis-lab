"""Jason Stys: synthetic differential demo or bounded local-data review with inert no-overwrite reports."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: save — line 40
# parameter: data — line 40
# parameter: path — line 40
# variable: descriptor — line 42
# variable: stream — line 43
# definition: render — line 47
# parameter: value — line 47
# variable: safe — line 49
# definition: read — line 57
# parameter: path — line 57
# variable: stream — line 61
# variable: value — line 62
# definition: main — line 68
# parameter: argv — line 68
# variable: parser — line 70
# variable: args — line 79
# variable: cases — line 81
# variable: value — line 84
# variable: data — line 86
# variable: name — line 86
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import subprocess
import sys
from pathlib import Path

from msal.core import MAX_BYTES, corpus
from msal.runner import compare


def save(path: Path, data: bytes) -> None:
    """Create a fresh owner-only file on POSIX without overwriting or following a file symlink."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)


def render(value: dict[str, object]) -> str:
    """Render escaped metadata JSON with CSP denying all scripts, frames, resources and forms."""
    safe = html.escape(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>Memory Safety Analysis Lab — Jason Stys</title></head><body><h1>Memory Safety Analysis Lab</h1><p>Created by Jason Stys. Help: docs/usage.md. Contact: github.com/JasonStys</p><p>Agreement and passing tests are evidence, not proof of universal memory safety. No arbitrary code is compiled or executed by this review.</p><pre>'
        + safe
        + "</pre></body></html>\n"
    )


def read(path: Path) -> bytes:
    """Read one explicit regular data file ≤1 MiB, defending against size changes before bounded read."""
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("input file/size")
    with path.open("rb") as stream:
        value = stream.read(MAX_BYTES + 1)
    if len(value) > MAX_BYTES:
        raise ValueError("input byte limit")
    return value


def main(argv: list[str] | None = None) -> int:
    """Compare the generated corpus or one data file; intentional unsafe specimens are never invoked."""
    parser = argparse.ArgumentParser(
        description="Safe C++/Rust memory analysis by Jason Stys"
    )
    parser.add_argument(
        "--input", type=Path, help="optional MSL1 data, never source code or executable"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="new private report directory"
    )
    args = parser.parse_args(argv)
    try:
        cases = (
            corpus() if args.input is None else [("provided-data", read(args.input))]
        )
        value = compare(cases)
        value["input_sha256"] = {
            name: hashlib.sha256(data).hexdigest() for name, data in cases
        }
        args.output.mkdir(parents=True, mode=0o700, exist_ok=False)
        save(
            args.output / "report.json",
            (json.dumps(value, indent=2, sort_keys=True) + "\n").encode(),
        )
        save(args.output / "report.html", render(value).encode())
        print(
            f"Compared {len(cases)} cases. Created by Jason Stys. Passed: {value['passed']}"
        )
        return 0 if value["passed"] else 1
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(
            f"Review stopped ({type(error).__name__}); check build, input limits and fresh output directory. No input data logged.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
