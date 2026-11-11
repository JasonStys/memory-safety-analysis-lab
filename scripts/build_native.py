"""Build the complete real offline workbench as one Windows portable executable. Jason Stys.

No publication, installation, shortcut change, host collection or Docker action.
"""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 39
# definition: main — line 43
# variable: version — line 52
# variable: source — line 55
# variable: dirty — line 58
# variable: output — line 63
# variable: release — line 63
# variable: vendor — line 101
# variable: resource_paths — line 110
# variable: name — line 124
# variable: metadata — line 126
# variable: name — line 134
# variable: path — line 134
# variable: command — line 140
# variable: name — line 161
# variable: path — line 161
# variable: command — line 164
# variable: command — line 165
# variable: executable — line 179
# variable: stream — line 180
# variable: digest — line 181
# END CODE MAP

import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

from native_common import icon, notices

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    """Freeze exact allowlisted public resources and bind actual source/dirty state without publishing."""
    if sys.platform != "win32" or sys.version_info[:3] != (3, 14, 10):
        raise RuntimeError(
            "This portable recipe requires patched Windows CPython3.14.10"
        )
    from msal import desktop_project as project
    from msal.desktop_io import read_bytes

    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    if version != project.VERSION:
        raise ValueError("Native version coherence failed")
    source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip()
    )
    release, output = ROOT / "release", ROOT / "out"
    release.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    # Compile only original default SAFE targets; deliberate specimens are never included.
    subprocess.run([sys.executable, "scripts/build.py"], cwd=ROOT, check=True)
    subprocess.run(
        [
            "cmake",
            "-S",
            str(ROOT),
            "-B",
            str(output / "cpp-native"),
            "-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded",
        ],
        cwd=ROOT,
        check=True,
        timeout=120,
    )
    subprocess.run(
        ["cmake", "--build", str(output / "cpp-native"), "--config", "Release"],
        cwd=ROOT,
        check=True,
        timeout=120,
    )
    subprocess.run(
        [
            "ctest",
            "--test-dir",
            str(output / "cpp-native"),
            "-C",
            "Release",
            "--output-on-failure",
        ],
        cwd=ROOT,
        check=True,
        timeout=30,
    )
    notices(release / "notices.txt")
    vendor = (ROOT / "licenses/RUST-COPYRIGHT-library.html").read_bytes()
    if len(vendor) > 4 * 1024 * 1024:
        raise ValueError("Actual Rust library notice exceeds its reviewed bound")
    (release / "notices.txt").write_bytes(
        (release / "notices.txt").read_bytes()
        + b"\n\nRust1.98.1 library inventory\n"
        + vendor
    )
    icon(output / "app.ico")
    resource_paths = {
        name: (
            release / name
            if name == "notices.txt"
            else output / name
            if name == "app.ico"
            else Path(sys.base_prefix) / name
            if name == "python314.dll"
            else output / "cpp-native/Release/parser-cpp.exe"
            if name == "runtime/parser-cpp.exe"
            else ROOT / "target/release/parser-rust.exe"
            if name == "runtime/parser-rust.exe"
            else ROOT / name
        )
        for name in project.RESOURCES
    }
    metadata = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": version,
        "source": source,
        "source_dirty": dirty,
        "resources": {
            name: hashlib.sha256(read_bytes(path, 32 * 1024 * 1024)).hexdigest()
            for name, path in resource_paths.items()
        },
    }
    (release / "native-release.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf8"
    )
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--icon",
        str(output / "app.ico"),
        "--name",
        "MemorySafetyAnalysisLab",
        "--distpath",
        "release/portable",
        "--workpath",
        "out/native-build",
        "--specpath",
        "out",
        "--paths",
        str(ROOT),
    ]
    for name, path in resource_paths.items():
        if name == "python314.dll":
            continue  # PyInstaller collects the actual interpreter DLL as a binary, not duplicate data.
        command += ["--add-data", str(path) + os.pathsep + Path(name).parent.as_posix()]
    command += [
        "--add-data",
        str(release / "native-release.json") + os.pathsep + ".",
        "scripts/native_entry.py",
    ]
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        env={
            **os.environ,
            "PYINSTALLER_CONFIG_DIR": str(output / "native-freezer-cache"),
        },
    )
    executable = release / "portable/MemorySafetyAnalysisLab.exe"
    with executable.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    executable.with_name(executable.name + ".sha256").write_text(
        digest + "  " + executable.name + "\n", encoding="ascii"
    )
    print(
        "Portable candidate built; source_dirty="
        + str(dirty)
        + "; not published or installed"
    )


if __name__ == "__main__":
    main()
