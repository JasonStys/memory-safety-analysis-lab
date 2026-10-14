"""Jason Stys: safe default-build isolation, private-state exclusion, action pins and exact local links."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 23
# definition: main — line 26
# variable: names — line 28
# variable: name — line 41
# variable: path — line 42
# variable: text — line 47
# variable: target — line 52
# variable: action — line 58
# variable: word — line 62
# variable: cmake — line 74
# variable: graph — line 76
# variable: codeql — line 83
# END CODE MAP

import json
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Validate every tracked file; expected faulty examples must stay outside all default build targets."""
    names = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    assert names != [""]
    assert {
        "msal/core.py",
        "msal/runner.py",
        "msal/cli.py",
        "msal/__init__.py",
    }.issubset(names)
    for name in names:
        path = ROOT / name
        assert path.is_file() and not name.startswith(
            ("out/", "target/", ".venv/", ".tools/")
        )
        assert not re.search(r"\.(?:pem|key|env|profraw|profdata)(?:$|[.-])", name)
        text = path.read_text(encoding="utf-8")
        assert not re.search(
            r"(?:ghp_|github_pat_)[A-Za-z0-9]{20,}|BEGIN [A-Z ]*PRIVATE KEY", text
        )
        if name.endswith(".md"):
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if not target.startswith(("http:", "https:", "#", "mailto:")):
                    assert (path.parent / target.split("#")[0]).is_file(), (
                        name + ": " + target
                    )
        if name.startswith(".github/workflows/"):
            for action in re.findall(r"uses:\s*([^\s#]+)", text):
                assert re.fullmatch(r"[\w/.-]+@[a-f0-9]{40}", action)
                assert not any(
                    word in action
                    for word in (
                        "upload-artifact",
                        "download-artifact",
                        "actions/cache",
                    )
                )
            assert (
                "persist-credentials: false" in text
                and "pull_request_target" not in text
            )
        if name.startswith("rust/"):
            assert not re.search(r"\bunsafe\s*\{", text)
    cmake = (ROOT / "CMakeLists.txt").read_text()
    assert "specimens/faults.cpp" not in cmake and "compile-fail/" not in cmake
    graph = tomllib.loads((ROOT / "Cargo.lock").read_text())
    assert len(graph["package"]) == 1 and "source" not in graph["package"][0]
    assert not tomllib.loads((ROOT / "pyproject.toml").read_text())["project"][
        "dependencies"
    ]
    assert "--hash=sha256:" in (ROOT / "requirements-dev.lock").read_text()
    assert "shell=True" not in (ROOT / "msal/runner.py").read_text()
    codeql = (ROOT / ".github/workflows/codeql.yml").read_text()
    assert "trap-caching: false" in codeql and "dependency-caching: false" in codeql
    assert len(json.loads((ROOT / "tools.lock.json").read_text())["tools"]) == 2
    print(f"Default-build isolation/privacy/pin/link gates: {len(names)} files passed")


if __name__ == "__main__":
    main()
