"""Jason Stys: explicit default-safe CMake and Rust release builds; no specimen targets or global installs."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 13
# definition: main — line 16
# variable: command — line 18
# variable: command — line 21
# END CODE MAP

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Configure safe native outputs with an installed CMake/compiler; failures stop before running tests."""
    command = ["cmake", "-S", str(ROOT), "-B", str(ROOT / "out/cpp")]
    # On Windows, preserve CMake's default/cached generator AND platform rather than forcing either.
    if os.name != "nt":
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
