"""Jason Stys: exact tracked-file README purpose inventory, unknown files fail rather than receive guesses."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 35
# variable: BEGIN — line 36
# variable: END — line 36
# variable: SPECIAL — line 37
# definition: purpose — line 55
# parameter: name — line 55
# variable: text — line 59
# variable: lines — line 64
# variable: index — line 65
# variable: line — line 65
# variable: description — line 67
# variable: continuation — line 69
# variable: description — line 75
# definition: main — line 80
# variable: parser — line 82
# variable: args — line 84
# variable: names — line 85
# variable: rows — line 93
# variable: name — line 94
# variable: label — line 95
# variable: path — line 97
# variable: original — line 98
# variable: end — line 99
# variable: start — line 99
# variable: expected — line 100
# END CODE MAP

import argparse
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- BEGIN FILE GUIDE -->", "<!-- END FILE GUIDE -->"
SPECIAL = {
    "licenses/MSVC-STL-LICENSE.txt": "Unmodified official Microsoft STL Apache-2.0 WITH LLVM-exception terms, matching installed header declarations.",
    "requirements-native.lock": "Exact hash-locked portable freezer graph, separate from the project runtime.",
    "licenses/RUST-COPYRIGHT-library.html": "Unmodified Rust standard-library copyright and dependency notices retained for the actual native worker.",
    "docs/reports/project-guide.docx": "Reviewed source-bound Word guide with dated validation observations and practical limits.",
    "docs/reports/publications.json": "Exact publication hashes, reviewed page identities and source/evidence baselines.",
    ".gitignore": "Exclude private diagnostics, builds, environments and generated fuzz artifacts.",
    ".gitattributes": "Consistent LF text checkouts across operating systems.",
    "Cargo.lock": "Complete dependency-free native Rust package graph.",
    "LICENSE": "MIT license for Jason Stys's authored code.",
    "requirements-dev.lock": "Universal full hash-locked Python development graph.",
    "tools.lock.json": "Official Linux scanner versions, URLs and SHA256 digests.",
    "docs/reports/ci.json": "Immutable accepted-source CI snapshot, not a future guarantee.",
    "docs/reports/sanitizers.json": "Actual normalized hosted sanitizer and Rust compile-rejection evidence.",
    "docs/reports/benchmark.json": "Measured release C++/Rust pipeline timing; no universal speed claim.",
}


def purpose(name: str) -> str:
    """Read the authored module/header/title purpose or explicit noncommentable-file description."""
    if name in SPECIAL:
        return SPECIAL[name]
    text = (ROOT / name).read_text(encoding="utf-8")
    if name.endswith(".py"):
        return (ast.get_docstring(ast.parse(text)) or "").splitlines()[0]
    if name.endswith(".md"):
        return text.splitlines()[0].lstrip("# ") + "."
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "Jason Stys:" in line:
            description = line.lstrip("#!/- ")
            if name.endswith((".cpp", ".hpp", ".rs")):
                for continuation in lines[index + 1 :]:
                    if (
                        not continuation.startswith("//")
                        or "BEGIN CODE MAP" in continuation
                    ):
                        break
                    description += " " + continuation.lstrip("/! ")
            return description
    raise ValueError("Tracked-file purpose missing: " + name)


def main() -> None:
    """Generate/check an exact full tracked-file table after staging only reviewed nonprivate files."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    names = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    if names == [""]:
        raise ValueError("Stage reviewed files first")
    rows = ["| File | Purpose |", "| --- | --- |"]
    for name in sorted(names):
        label = name.replace("_", "\\_")
        rows.append(f"| [{label}]({name}) | {purpose(name).replace('|', '/')} |")
    path = ROOT / "README.md"
    original = path.read_text(encoding="utf-8")
    start, end = original.index(BEGIN) + len(BEGIN), original.index(END)
    expected = original[:start] + "\n\n" + "\n".join(rows) + "\n\n" + original[end:]
    if args.check and expected != original:
        raise ValueError("README file guide stale")
    if not args.check:
        path.write_text(expected, encoding="utf-8", newline="\n")
    print(f"README complete inventory: {len(names)}")


if __name__ == "__main__":
    main()
