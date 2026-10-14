"""Jason Stys: actual worker/CLI privacy, no-overwrite output and process/batch failure regressions."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_complete_demo — line 60
# parameter: tmp_path — line 60
# variable: output — line 62
# variable: value — line 64
# definition: test_one_input — line 73
# parameter: tmp_path — line 73
# variable: source — line 75
# variable: data — line 76
# variable: output — line 78
# variable: value — line 80
# definition: test_failed_comparison — line 87
# parameter: monkeypatch — line 87
# parameter: tmp_path — line 87
# parameter: cases — line 89
# definition: test_inputs_and_output — line 94
# parameter: monkeypatch — line 94
# parameter: tmp_path — line 94
# variable: value — line 98
# variable: original — line 105
# definition: report_smaller — line 107
# parameter: args — line 107
# parameter: kwargs — line 107
# parameter: self — line 107
# variable: result — line 109
# definition: test_workers_errors — line 130
# parameter: capsys — line 130
# parameter: monkeypatch — line 130
# parameter: tmp_path — line 130
# variable: language — line 136
# variable: path — line 137
# definition: timeout — line 141
# parameter: args — line 141
# parameter: kwargs — line 141
# parameter: args — line 150
# parameter: kwargs — line 150
# definition: test_actual_transport_errors — line 158
# variable: language — line 160
# variable: data — line 161
# variable: value — line 167
# definition: test_inert_report — line 177
# variable: value — line 179
# END CODE MAP

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from msal import cli, runner
from msal.cli import main, read, render, save
from msal.core import MAX_BYTES, packet
from msal.runner import executable


def test_complete_demo(tmp_path):
    """Generate actual metadata/HTML reports and verify that faulty specimens are never invoked."""
    output = tmp_path / "review"
    assert main(["--output", str(output)]) == 0
    value = json.loads((output / "report.json").read_text())
    assert value["passed"] and value["case_count"] == 243
    assert value["author"] == "Jason Stys"
    assert "specimen" not in json.dumps(value)
    assert main(["--output", str(output)]) == 2
    if os.name != "nt":
        assert (output / "report.json").stat().st_mode & 0o077 == 0


def test_one_input(tmp_path):
    """Hash and analyze the same bounded file bytes; report never exports payload text or source path."""
    source = tmp_path / "private-name.bin"
    data = packet([(2, b"PRIVATE-SYNTHETIC")])
    source.write_bytes(data)
    output = tmp_path / "review"
    assert main(["--input", str(source), "--output", str(output)]) == 0
    value = json.loads((output / "report.json").read_text())
    assert value["input_sha256"]["provided-data"] == hashlib.sha256(data).hexdigest()
    assert "PRIVATE-SYNTHETIC" not in json.dumps(
        value
    ) and "private-name" not in json.dumps(value)


def test_failed_comparison(tmp_path, monkeypatch):
    """A detected mismatch remains an explicit failed review, not a silently successful score."""
    monkeypatch.setattr(cli, "compare", lambda cases: {"passed": False})
    assert main(["--output", str(tmp_path / "review")]) == 1
    assert json.loads((tmp_path / "review/report.json").read_text())["passed"] is False


def test_inputs_and_output(tmp_path, monkeypatch):
    """Directory/oversize/growing inputs, file symlinks and output overwrites are rejected."""
    with pytest.raises(ValueError):
        read(tmp_path)
    value = tmp_path / "data"
    save(value, b"safe")
    with pytest.raises(FileExistsError):
        save(value, b"replacement")
    value.write_bytes(b"x" * (MAX_BYTES + 1))
    with pytest.raises(ValueError):
        read(value)
    original = Path.stat

    def report_smaller(self, *args, **kwargs):
        """Model size changing before bounded read without introducing a filesystem race."""
        result = original(self, *args, **kwargs)
        return os.stat_result(
            (
                result.st_mode,
                result.st_ino,
                result.st_dev,
                result.st_nlink,
                result.st_uid,
                result.st_gid,
                0,
                result.st_atime,
                result.st_mtime,
                result.st_ctime,
            )
        )

    monkeypatch.setattr(Path, "stat", report_smaller)
    with pytest.raises(ValueError, match="byte limit"):
        read(value)


def test_workers_errors(tmp_path, monkeypatch, capsys):
    """Missing builds, unknown workers, deadlines and native crashes have controlled private diagnostics."""
    with pytest.raises(ValueError):
        executable("arbitrary")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    assert main(["--output", str(tmp_path / "out")]) == 2
    for language in ["cpp", "rust"]:
        path = executable(language)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    def timeout(*args, **kwargs):
        """Inject a worker deadline without waiting for an actual hung process."""
        raise subprocess.TimeoutExpired("trusted worker", 15)

    monkeypatch.setattr(subprocess, "run", timeout)
    assert main(["--output", str(tmp_path / "out")]) == 2
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            [], 2, b"", b"private data"
        ),
    )
    assert main(["--output", str(tmp_path / "out")]) == 2
    assert "private data" not in capsys.readouterr().err


def test_actual_transport_errors():
    """Both actual workers reject truncated/oversize/cardinality-invalid batches with no partial stdout."""
    for language in ["cpp", "rust"]:
        for data in [
            b"x",
            (MAX_BYTES + 1).to_bytes(4, "little"),
            b"\0" * 4 * 1001,
            b"x" * (8 * MAX_BYTES + 1),
        ]:
            value = subprocess.run(
                [str(executable(language))],
                input=data,
                capture_output=True,
                timeout=15,
                check=False,
            )
            assert value.returncode == 2 and not value.stdout


def test_inert_report():
    """Adversarial JSON strings stay escaped text; no scripts/frames/network resources are generated."""
    value = render(
        {"data": '</pre><script>alert(1)</script><img src="https://example.com">'}
    )
    assert (
        "<script>" not in value and "<img " not in value and "&lt;script&gt;" in value
    )
    assert "default-src 'none'" in value and "Jason Stys" in value
