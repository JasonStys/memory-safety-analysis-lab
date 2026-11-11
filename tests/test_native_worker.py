"""Frozen fixed-worker authority, exact transport, timeout ownership and source dispatch controls. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: native — line 70
# parameter: monkeypatch — line 70
# parameter: tmp_path — line 70
# variable: name — line 73
# variable: path — line 74
# parameter: _args — line 79
# definition: test_owned_worker_keeps_data_argv_environment_and_cleanup_distinct — line 86
# parameter: fault — line 87
# parameter: monkeypatch — line 87
# parameter: native — line 87
# variable: events — line 90
# definition: Process — line 92
# variable: returncode — line 95
# definition: communicate — line 97
# parameter: input — line 97
# parameter: self — line 97
# parameter: timeout — line 97
# attribute: returncode — line 106
# definition: poll — line 114
# parameter: self — line 114
# definition: kill — line 118
# parameter: self — line 118
# attribute: returncode — line 121
# variable: process — line 123
# definition: launch — line 125
# parameter: argv — line 125
# parameter: kwargs — line 125
# definition: test_invalid_authority_and_limits_fail_before_any_process — line 164
# parameter: fault — line 165
# parameter: monkeypatch — line 165
# parameter: native — line 165
# parameter: _args — line 171
# parameter: _kwargs — line 171
# variable: data — line 173
# variable: path — line 173
# variable: timeout — line 173
# variable: path — line 175
# variable: data — line 177
# variable: timeout — line 179
# definition: test_identity_failure_refuses_before_execution — line 189
# parameter: monkeypatch — line 189
# parameter: native — line 189
# parameter: _args — line 194
# variable: _ — line 194
# parameter: _args — line 199
# parameter: _kwargs — line 199
# definition: test_frozen_runner_dispatches_only_fixed_workers_and_validates_original_protocol — line 205
# parameter: monkeypatch — line 206
# parameter: native — line 206
# variable: observed — line 211
# definition: complete — line 213
# parameter: data — line 213
# parameter: path — line 213
# parameter: timeout — line 213
# END CODE MAP

import subprocess

import pytest

from msal import desktop_project as project
from msal import desktop_state, native_worker, runner
from msal.core import Outcome
from msal.desktop_io import Rejected


@pytest.fixture
def native(tmp_path, monkeypatch):
    """Use inert worker files; full frozen acceptance separately executes actual compiled safe binaries."""
    monkeypatch.setattr(project, "ROOT", tmp_path)
    for name in ("parser-cpp.exe", "parser-rust.exe"):
        path = tmp_path / "runtime" / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"inert owned boundary fixture - not executed")
    # Complete metadata/hash verification has independent real-file fixtures in test_desktop_state;
    # isolate only this owned-process boundary, never forge the native consumer's reports.
    monkeypatch.setattr(desktop_state, "package_identity", lambda *_args: {})
    return tmp_path / "runtime/parser-cpp.exe"


@pytest.mark.parametrize(
    "fault", [None, "exit", "oversize", "timeout", "communicate-error"]
)
def test_owned_worker_keeps_data_argv_environment_and_cleanup_distinct(
    native, monkeypatch, fault
):
    """Neither a collector exit/output failure nor timeout is parser evidence; only this created process is cleaned up."""
    events = []

    class Process:
        """An inert child boundary with explicit lifecycle; original safe workers are exercised by independent native tests."""

        returncode = None

        def communicate(self, *, input=None, timeout):
            """Observe exact binary stdin and original deadlines, without invoking a compiler or foreign program."""
            events.append((input, timeout))
            if len(events) == 1:
                if fault == "timeout":
                    raise subprocess.TimeoutExpired("owned fixture", timeout)
                if fault == "communicate-error":
                    raise OSError("inert authored transport failure")
                assert input == b"\x04\x00\x00\x00MSL1" and timeout == 15
                self.returncode = 7 if fault == "exit" else 0
            return (
                b"x" * (128 * 1024 + 1)
                if fault == "oversize"
                else b"MSAL\t1\nERR\theader\n",
                None,
            )

        def poll(self):
            """Keep failure paths visibly live until this exact owned process is killed/drained."""
            return self.returncode

        def kill(self):
            """Record cleanup of the one newly created boundary fixture."""
            events.append("owned-kill")
            self.returncode = -9

    process = Process()

    def launch(argv, **kwargs):
        """Assert a closed executable, binary pipe contract and absence of user/provider/loader configuration."""
        assert argv == [str(native)]
        assert kwargs["stdin"] == kwargs["stdout"] == subprocess.PIPE
        assert kwargs["stderr"] == subprocess.DEVNULL
        assert "OPENAI_API_KEY" not in kwargs["env"]
        assert "PYTHONPATH" not in kwargs["env"]
        assert "UNTRUSTED" not in kwargs["env"]["PATH"]
        assert kwargs["cwd"] == native.parent.parent
        return process

    monkeypatch.setenv("OPENAI_API_KEY", "PRIVATE-INERT")
    monkeypatch.setenv("PYTHONPATH", "UNTRUSTED")
    monkeypatch.setattr(native_worker.subprocess, "Popen", launch)
    if fault is None:
        assert (
            native_worker.run_owned(native, b"\x04\x00\x00\x00MSL1", 15)
            == b"MSAL\t1\nERR\theader\n"
        )
    else:
        with pytest.raises((Rejected, subprocess.TimeoutExpired, OSError)):
            native_worker.run_owned(native, b"\x04\x00\x00\x00MSL1", 15)
    if fault in ("timeout", "communicate-error"):
        assert "owned-kill" in events and events[-1] == (None, 5)
    else:
        assert "owned-kill" not in events


@pytest.mark.parametrize(
    "fault",
    [
        "foreign-program",
        "oversized-data",
        "bool-timeout",
        "zero-timeout",
        "over-timeout",
        "nan-timeout",
    ],
)
def test_invalid_authority_and_limits_fail_before_any_process(
    native, monkeypatch, fault
):
    """No caller path, huge data or malformed deadline can enter the fixed executable boundary."""
    monkeypatch.setattr(
        native_worker.subprocess,
        "Popen",
        lambda *_args, **_kwargs: pytest.fail("invalid request executed"),
    )
    path, data, timeout = native, b"", 15
    if fault == "foreign-program":
        path = native.parent / "foreign.exe"
    elif fault == "oversized-data":
        data = b"x" * (8 * 1024 * 1024 + 1)
    else:
        timeout = {
            "bool-timeout": True,
            "zero-timeout": 0,
            "over-timeout": 16,
            "nan-timeout": float("nan"),
        }[fault]
    with pytest.raises(Rejected):
        native_worker.run_owned(path, data, timeout)


def test_identity_failure_refuses_before_execution(native, monkeypatch):
    """A changed package resource cannot be papered over by a successful process return code."""
    monkeypatch.setattr(
        desktop_state,
        "package_identity",
        lambda *_args: (_ for _ in ()).throw(Rejected("changed admitted resource")),
    )
    monkeypatch.setattr(
        native_worker.subprocess,
        "Popen",
        lambda *_args, **_kwargs: pytest.fail("unadmitted bytes executed"),
    )
    with pytest.raises(Rejected, match="changed admitted resource"):
        native_worker.run_owned(native, b"", 15)


def test_frozen_runner_dispatches_only_fixed_workers_and_validates_original_protocol(
    native, monkeypatch
):
    """The existing runner consumes actual boundary bytes through its original strict protocol parser."""
    monkeypatch.setattr(runner.sys, "frozen", True, raising=False)
    monkeypatch.setattr(runner, "ROOT", native.parent.parent)
    observed = []

    def complete(path, data, timeout):
        """Return one literal native protocol record; no parser oracle/result object is supplied by this boundary fixture."""
        observed.append((path, data, timeout))
        return b"MSAL\t1\nERR\theader\n"

    monkeypatch.setattr(native_worker, "run_owned", complete)
    assert runner.run("cpp", [b"MSL1"]) == [Outcome("error", "header")]
    assert observed == [(native, b"\x04\x00\x00\x00MSL1", 15)]
    assert runner.executable("rust") == native.parent / "parser-rust.exe"
    with pytest.raises(ValueError, match="unknown worker"):
        runner.executable("foreign")
