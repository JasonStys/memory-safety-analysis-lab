"""Jason Stys: actual coverage-guided libFuzzer campaign on safe C++ parser, never faulty specimens."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 20
# definition: main — line 23
# variable: output — line 25
# variable: seeds — line 26
# variable: _ — line 28
# variable: data — line 28
# variable: index — line 28
# variable: executable — line 30
# END CODE MAP

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from msal.core import corpus

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Build ASan/UBSan libFuzzer, seed bounded synthetic cases and require 20,000 runs without a crash."""
    output = ROOT / "out/fuzz"
    seeds = output / "corpus"
    seeds.mkdir(parents=True, exist_ok=True, mode=0o700)
    for index, (_, data) in enumerate(corpus()):
        (seeds / f"seed-{index:04d}").write_bytes(data)
    executable = output / "parser-fuzzer"
    subprocess.run(
        [
            "clang++-18",
            "-std=c++20",
            "-O1",
            "-g",
            "-fno-omit-frame-pointer",
            "-fsanitize=fuzzer,address,undefined",
            "-fno-sanitize-recover=all",
            "-I",
            "native",
            "native/safe.cpp",
            "native/fuzz.cpp",
            "-o",
            str(executable),
        ],
        cwd=ROOT,
        timeout=120,
        check=True,
    )
    subprocess.run(
        [
            str(executable),
            str(seeds),
            "-runs=20000",
            "-seed=12345",
            "-max_len=65536",
            "-timeout=2",
            "-rss_limit_mb=1024",
            f"-artifact_prefix={output}/",
        ],
        cwd=ROOT,
        timeout=180,
        check=True,
    )
    print(
        "20,000 coverage-guided libFuzzer runs completed without a sanitizer crash; not a safety proof."
    )


if __name__ == "__main__":
    main()
