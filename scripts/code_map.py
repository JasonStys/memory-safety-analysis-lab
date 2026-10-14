"""Jason Stys: generate exact definition/variable line maps and verify Python function/class contracts."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 59
# definition: mapped — line 62
# parameter: source — line 62
# parameter: suffix — line 62
# variable: prefix — line 64
# variable: begin — line 67
# variable: end — line 67
# variable: source — line 68
# variable: lines — line 74
# variable: records — line 75
# variable: tree — line 77
# variable: first — line 78
# variable: insertion — line 79
# variable: node — line 86
# variable: insertion — line 98
# variable: insertion — line 100
# variable: line — line 101
# variable: number — line 101
# variable: name — line 104
# variable: name — line 106
# variable: name — line 108
# variable: name — line 110
# variable: kind — line 113
# variable: name — line 113
# variable: name — line 117
# variable: binding — line 121
# variable: name — line 122
# variable: binding — line 125
# variable: name — line 126
# variable: kind — line 129
# variable: name — line 129
# variable: name — line 133
# variable: name — line 144
# variable: name — line 149
# variable: name — line 152
# variable: count — line 154
# variable: header — line 155
# variable: kind — line 159
# variable: name — line 159
# variable: number — line 159
# parameter: item — line 160
# definition: main — line 169
# variable: parser — line 171
# variable: args — line 173
# variable: paths — line 174
# variable: stale — line 186
# variable: path — line 187
# variable: original — line 188
# variable: expected — line 189
# END CODE MAP

import argparse
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mapped(source: str, suffix: str) -> str:
    """Parse Python AST or lexical C++/Rust/CMake/workflow declarations without executing authored source."""
    prefix = (
        "--" if suffix == ".sql" else "//" if suffix in {".rs", ".cpp", ".hpp"} else "#"
    )
    begin, end = prefix + " BEGIN CODE MAP", prefix + " END CODE MAP"
    source = re.sub(
        r"^" + re.escape(begin) + r"[^\n]*\n.*?^" + re.escape(end) + r"\n",
        "",
        source,
        flags=re.M | re.S,
    )
    lines = source.splitlines(keepends=True)
    records = set()
    if suffix == ".py":
        tree = ast.parse(source)
        first = tree.body[0] if tree.body else None
        insertion = (
            first.end_lineno
            if isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
            else 0
        )
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    raise ValueError(f"Missing function/class description: {node.name}")
                records.add(("definition", node.name, node.lineno))
            elif isinstance(node, ast.arg):
                records.add(("parameter", node.arg, node.lineno))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                records.add(("variable", node.id, node.lineno))
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                records.add(("attribute", node.attr, node.lineno))
    else:
        insertion = 1 if source.startswith(("#!", "<?php", "/**", "//")) else 0
        while insertion < len(lines) and lines[insertion].startswith(prefix):
            insertion += 1
        for number, line in enumerate(lines, 1):
            if line.lstrip().startswith(prefix):
                continue
            for name in re.findall(r"^\s*(?:- )?([\w-]+):", line):
                records.add(("parameter", name, number))
            for name in re.findall(r"CREATE (?:TABLE|TRIGGER|INDEX) (\w+)", line):
                records.add(("SQL object", name, number))
            for name in re.findall(r"\b(\w+) (?:INTEGER|TEXT|BLOB)\b", line):
                records.add(("column", name, number))
            for name in re.findall(r"\$([A-Za-z_][A-Za-z0-9_]*)", line):
                records.add(("variable", name, number))
            if suffix == ".rs":
                for kind, name in re.findall(
                    r"\b(fn|struct|enum|const|mod)\s+([A-Za-z_]\w*)", line
                ):
                    records.add((kind, name, number))
                for name in re.findall(
                    r"(?:pub\s+)?([a-z_]\w*)\s*:\s*(?:&|[A-Za-z_])", line
                ):
                    records.add(("field/parameter", name, number))
                for binding in re.findall(r"\blet\s+(?:mut\s+)?([^=;]+)", line):
                    for name in re.findall(r"\b[a-z_]\w*\b", binding.split(":")[0]):
                        if name != "mut":
                            records.add(("binding", name, number))
                for binding in re.findall(r"\bfor\s+(.+?)\s+in\b", line):
                    for name in re.findall(r"\b[a-z_]\w*\b", binding):
                        records.add(("loop binding", name, number))
            if suffix in {".cpp", ".hpp"}:
                for kind, name in re.findall(
                    r"\b(class|struct|namespace)\s+([A-Za-z_]\w*)", line
                ):
                    records.add((kind, name, number))
                for name in re.findall(
                    r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:const\s*)?(?:;|\{)", line
                ):
                    if name not in {
                        "if",
                        "for",
                        "while",
                        "switch",
                        "return",
                    }:
                        records.add(("function occurrence", name, number))
                for name in re.findall(
                    r"\b(?:auto|size_t|uint64_t|uint8_t|unsigned|int|char|bool|string|Handle|Slot)\s*(?:&|\*)?\s*([A-Za-z_]\w*)",
                    line,
                ):
                    records.add(("binding/parameter", name, number))
                for name in re.findall(r"\b([a-z_]\w*)\s*=\s*(?!=)", line):
                    records.add(("binding", name, number))
            if suffix == ".txt":
                for name in re.findall(r"^(\w+)\(", line):
                    records.add(("CMake command", name, number))
    count = len(records) + 2
    header = [
        begin + " (generated; python scripts/code_map.py)",
        *[
            f"{prefix} {kind}: {name} — line {number + count if number > insertion else number}"
            for kind, name, number in sorted(
                records, key=lambda item: (item[2], item[0], item[1])
            )
        ],
        end,
    ]
    lines.insert(insertion, "\n".join(header) + "\n")
    return "".join(lines)


def main() -> int:
    """Generate/check all authored Python and operational declarative files; stale headers fail CI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    paths = [
        *(ROOT / "msal").glob("*.py"),
        *(ROOT / "scripts").glob("*.py"),
        *(ROOT / "tests").glob("*.py"),
        *(ROOT / "rust").glob("*.rs"),
        *(ROOT / "compile-fail").glob("*.rs"),
        *(ROOT / "native").glob("*.cpp"),
        *(ROOT / "native").glob("*.hpp"),
        *(ROOT / "specimens").glob("*.cpp"),
        ROOT / "CMakeLists.txt",
        *(ROOT / ".github/workflows").glob("*.yml"),
    ]
    stale = []
    for path in paths:
        original = path.read_text(encoding="utf-8")
        expected = mapped(original, path.suffix)
        if original != expected:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(expected, encoding="utf-8", newline="\n")
    print("Code maps current" if not stale else "Code maps: " + ", ".join(stale))
    return int(args.check and bool(stale))


if __name__ == "__main__":
    raise SystemExit(main())
