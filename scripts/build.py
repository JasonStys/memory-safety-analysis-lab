"""Jason Stys: explicit default-safe CMake and Rust release builds; no specimen targets or global installs."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 14
# definition: main — line 17
# variable: command — line 19
# variable: command — line 21
# variable: command — line 23
# END CODE MAP

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Configure safe native outputs with an installed CMake/compiler; failures stop before running tests."""
    command = ["cmake", "-S", str(ROOT), "-B", str(ROOT / "out/cpp")]
    if os.name == "nt":
        command += ["-G", "Visual Studio 17 2022"]
    else:
        command += ["-DCMAKE_BUILD_TYPE=Release"]
    subprocess.run(command, check=True, timeout=120)
    subprocess.run(
        ["cmake", "--build", str(ROOT / "out/cpp"), "--config", "Release"],
        check=True,
        timeout=120,
    )
    subprocess.run(
        [
            "ctest",
            "--test-dir",
            str(ROOT / "out/cpp"),
            "-C",
            "Release",
            "--output-on-failure",
        ],
        check=True,
        timeout=30,
    )
    subprocess.run(
        ["cargo", "build", "--release", "--locked"], cwd=ROOT, check=True, timeout=120
    )


if __name__ == "__main__":
    main()
