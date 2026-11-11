"""Build the complete real offline workbench as one Windows portable executable. Jason Stys.

No publication, installation, shortcut change, host collection or Docker action.
"""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 42
# definition: main — line 46
# variable: version — line 55
# variable: source — line 58
# variable: dirty — line 61
# variable: output — line 66
# variable: release — line 66
# variable: expected — line 104
# variable: label — line 104
# variable: name — line 104
# variable: vendor — line 116
# variable: resource_paths — line 131
# variable: name — line 145
# variable: metadata — line 147
# variable: name — line 155
# variable: path — line 155
# variable: command — line 161
# variable: name — line 182
# variable: path — line 182
# variable: command — line 185
# variable: command — line 186
# variable: executable — line 200
# variable: stream — line 201
# variable: digest — line 202
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
    for label, name, expected in (
        (
            "Rust1.98.1 library inventory",
            "RUST-COPYRIGHT-library.html",
            "68129500b616d5838629e68f55ff3aed5e096dacf60ce9eb41bbe599a563afa6",
        ),
        (
            "Microsoft C++ Standard Library / Apache2.0 WITH LLVM-exception",
            "MSVC-STL-LICENSE.txt",
            "1fc6b6db121d4555d8f661937d7f6013693cd8fd67495d5e5d98c1d18fb83eda",
        ),
    ):
        vendor = (ROOT / "licenses" / name).read_bytes()
        if (
            len(vendor) > 4 * 1024 * 1024
            or hashlib.sha256(vendor).hexdigest() != expected
        ):
            raise ValueError("Actual native library notice identity changed")
        (release / "notices.txt").write_bytes(
            (release / "notices.txt").read_bytes()
            + b"\n\n"
            + label.encode()
            + b"\n"
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
