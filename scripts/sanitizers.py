"""Jason Stys: explicit trusted Linux specimen assertions, safe runtime sanitizer checks and coverage."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 59
# variable: CASES — line 60
# definition: execute — line 70
# parameter: command — line 70
# parameter: kwargs — line 70
# definition: main — line 75
# variable: parser — line 77
# variable: output — line 84
# variable: environment — line 86
# variable: compiler — line 92
# variable: rows — line 97
# variable: cwe — line 98
# variable: expected — line 98
# variable: instrumentation — line 98
# variable: number — line 98
# variable: executable — line 99
# variable: completed — line 115
# variable: diagnostic — line 122
# variable: matched — line 123
# variable: expected — line 138
# variable: source — line 138
# variable: completed — line 139
# variable: diagnostic — line 151
# variable: profile — line 161
# variable: _ — line 179
# variable: data — line 179
# variable: values — line 179
# variable: completed — line 180
# variable: data — line 187
# variable: data — line 189
# variable: completed — line 196
# variable: path — line 206
# variable: raw — line 206
# variable: coverage — line 217
# variable: measured — line 228
# variable: runtime — line 229
# variable: item — line 231
# variable: item — line 235
# variable: line_total — line 235
# variable: item — line 236
# variable: line_covered — line 236
# variable: result — line 238
# variable: row — line 242
# END CODE MAP

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from msal.core import batch, corpus, outcomes, reference

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    (1, "CWE-125", "address", "heap-buffer-overflow"),
    (2, "CWE-125", "address", "stack-buffer-overflow"),
    (3, "CWE-416", "address", "heap-use-after-free"),
    (4, "CWE-415", "address", "attempting double-free"),
    (5, "CWE-401", "address", "detected memory leaks"),
    (6, "CWE-190", "undefined", "signed integer overflow"),
]


def execute(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run one fixed trusted command with bounded wall time; never a shell or user code."""
    return subprocess.run(command, cwd=ROOT, timeout=120, check=True, **kwargs)


def main() -> None:
    """Require explicit opt-in and Linux; prove expected defect signals and clean repaired runtime."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-trusted-specimens", action="store_true", required=True)
    parser.parse_args()
    if platform.system() != "Linux":
        raise SystemExit(
            "Linux-only sanitizer harness; safe default workers are portable."
        )
    output = ROOT / "out/assurance"
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    environment = dict(
        os.environ,
        ASAN_OPTIONS="detect_leaks=1:halt_on_error=1:exitcode=86",
        LSAN_OPTIONS="exitcode=87",
        UBSAN_OPTIONS="halt_on_error=1:exitcode=88:print_stacktrace=1",
    )
    compiler = (
        execute(["clang++-18", "--version"], capture_output=True)
        .stdout.decode()
        .splitlines()[0]
    )
    rows = []
    for number, cwe, instrumentation, expected in CASES:
        executable = output / f"specimen-{number}"
        execute(
            [
                "clang++-18",
                "-std=c++20",
                "-O0",
                "-g",
                "-fno-omit-frame-pointer",
                "-fno-sanitize-recover=all",
                f"-fsanitize={instrumentation}",
                f"-DMSAL_CASE={number}",
                "specimens/faults.cpp",
                "-o",
                str(executable),
            ]
        )
        completed = subprocess.run(
            [str(executable)],
            env=environment,
            capture_output=True,
            timeout=10,
            check=False,
        )
        diagnostic = completed.stderr.decode("utf-8", errors="replace")
        matched = (
            completed.returncode != 0
            and expected in diagnostic
            and len(diagnostic) <= 1024 * 1024
        )
        (output / f"specimen-{number}.stderr").write_text(diagnostic, encoding="utf-8")
        rows.append(
            {
                "case": f"specimen-{number}",
                "cwe": cwe,
                "expected_signal": expected,
                "exit_code": completed.returncode,
                "matched": matched,
            }
        )
    for source, expected in [("moved", "E0382"), ("borrowed", "E0502")]:
        completed = subprocess.run(
            [
                "rustc",
                "--edition=2024",
                f"compile-fail/{source}.rs",
                "-o",
                str(output / source),
            ],
            capture_output=True,
            timeout=30,
            check=False,
        )
        diagnostic = completed.stderr.decode("utf-8", errors="replace")
        rows.append(
            {
                "case": source,
                "expected_signal": expected,
                "exit_code": completed.returncode,
                "matched": completed.returncode != 0
                and f"error[{expected}]" in diagnostic,
            }
        )
    profile = ROOT / "out/coverage"
    profile.mkdir(exist_ok=True, mode=0o700)
    environment["LLVM_PROFILE_FILE"] = str(profile / "%p.profraw")
    execute(
        [
            "cmake",
            "-S",
            ".",
            "-B",
            "out/sanitized",
            "-DCMAKE_CXX_COMPILER=clang++-18",
            "-DCMAKE_BUILD_TYPE=Debug",
            "-DMSAL_SANITIZE=ON",
            "-DMSAL_COVERAGE=ON",
        ]
    )
    execute(["cmake", "--build", "out/sanitized", "--parallel", "2"])
    execute(["out/sanitized/test-cpp"], env=environment)
    values = [data for _, data in corpus()]
    completed = execute(
        ["out/sanitized/parser-cpp"],
        input=batch(values),
        env=environment,
        capture_output=True,
    )
    assert outcomes(completed.stdout, len(values)) == [
        reference(data) for data in values
    ]
    for data in [
        b"",
        b"x",
        b"\0" * 4 * 1001,
        (1024 * 1024 + 1).to_bytes(4, "little"),
        b"\0" * (8 * 1024 * 1024 + 1),
    ]:
        completed = subprocess.run(
            ["out/sanitized/parser-cpp"],
            input=data,
            env=environment,
            capture_output=True,
            timeout=15,
            check=False,
        )
        assert completed.returncode == (0 if not data else 2)
        assert b"Sanitizer" not in completed.stderr
    raw = [str(path) for path in profile.glob("*.profraw")]
    execute(
        [
            "llvm-profdata-18",
            "merge",
            "-sparse",
            *raw,
            "-o",
            str(profile / "merged.profdata"),
        ]
    )
    coverage = execute(
        [
            "llvm-cov-18",
            "export",
            "out/sanitized/test-cpp",
            "-object",
            "out/sanitized/parser-cpp",
            f"-instr-profile={profile / 'merged.profdata'}",
        ],
        capture_output=True,
    )
    measured = json.loads(coverage.stdout)
    runtime = [
        item
        for item in measured["data"][0]["files"]
        if Path(item["filename"]).name in {"safe.cpp", "main.cpp"}
    ]
    assert len(runtime) == 2
    line_total = sum(item["summary"]["lines"]["count"] for item in runtime)
    line_covered = sum(item["summary"]["lines"]["covered"] for item in runtime)
    assert line_covered / line_total >= 0.95
    result = {
        "schema": "msal-native-assurance-v1",
        "author": "Jason Stys",
        "compiler": compiler,
        "passed": all(row["matched"] for row in rows),
        "specimen_assertions": rows,
        "clean_safe_cpp": True,
        "safe_cpp_line_coverage_percent": 100 * line_covered / line_total,
        "coverage_files": ["native/safe.cpp", "native/main.cpp"],
        "limits": "Trusted synthetic specimens in separate hosted processes; not an OS sandbox or arbitrary-code analysis.",
    }
    (output / "sanitizers.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(
            "Expected specimen/compile-rejection diagnostic was absent; gate failed."
        )


if __name__ == "__main__":
    main()
