"""Owned fixed safe-parser process boundary for the frozen app, never arbitrary user code. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: run_owned — line 27
# parameter: data — line 27
# parameter: path — line 27
# parameter: timeout — line 27
# variable: names — line 32
# variable: identity — line 45
# variable: environment — line 50
# variable: key — line 52
# variable: process — line 59
# variable: _ — line 70
# variable: output — line 70
# END CODE MAP

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from .desktop_io import Rejected
from .inputs import file_hash


def run_owned(path: Path, data: bytes, timeout: float) -> bytes:
    """Rebind actual admitted worker bytes before execution; use fixed argv/minimal environment and owned timeout cleanup."""
    from . import desktop_project as project
    from .desktop_state import package_identity

    names = {
        project.ROOT / "runtime/parser-cpp.exe",
        project.ROOT / "runtime/parser-rust.exe",
    }
    if (
        path not in names
        or not isinstance(data, bytes)
        or len(data) > 8 * 1024 * 1024
        or isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 0.001 <= timeout <= 15
    ):
        raise Rejected("only bounded data for fixed safe parsers is accepted")
    identity = package_identity(
        project.ROOT, project.PRODUCT, project.VERSION, project.RESOURCES
    )
    del identity  # package_identity validates the complete closed resource set against actual frozen bytes.
    file_hash(path, 32 * 1024 * 1024)
    environment = {
        key: os.environ[key]
        for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP")
        if key in os.environ
    }
    environment["PATH"] = str(
        Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "System32"
    )
    # These self-contained authored safe workers never load a user plugin or runtime configuration.
    process = subprocess.Popen(
        [str(path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=environment,
        cwd=project.ROOT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        try:
            output, _ = process.communicate(input=data, timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except OSError:
                pass
            try:
                process.communicate(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                pass  # The final owned cleanup below retains the original failure.
            raise
        if process.returncode != 0 or len(output) > 128 * 1024:
            raise Rejected("owned safe worker failed or exceeded output contract")
        return output
    finally:
        # No independently discovered process/listener is adopted or signaled.
        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                pass
            try:
                process.communicate(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                # A requested kill or two expired drains is not exit proof. Keep
                # this same GUI worker/profile alive until the exact child is
                # reaped, then propagate the original analysis failure.
                while True:
                    try:
                        process.communicate(timeout=1)
                        break
                    except (subprocess.TimeoutExpired, OSError):
                        time.sleep(0.05)
