"""Frozen fixed-worker authority, exact transport, timeout ownership and source dispatch controls. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: native — line 99
# parameter: monkeypatch — line 99
# parameter: tmp_path — line 99
# variable: name — line 102
# variable: path — line 103
# parameter: _args — line 108
# definition: test_owned_worker_keeps_data_argv_environment_and_cleanup_distinct — line 115
# parameter: fault — line 116
# parameter: monkeypatch — line 116
# parameter: native — line 116
# variable: events — line 119
# definition: Process — line 121
# variable: returncode — line 124
# definition: communicate — line 126
# parameter: input — line 126
# parameter: self — line 126
# parameter: timeout — line 126
# attribute: returncode — line 135
# definition: poll — line 143
# parameter: self — line 143
# definition: kill — line 147
# parameter: self — line 147
# attribute: returncode — line 150
# variable: process — line 152
# definition: launch — line 154
# parameter: argv — line 154
# parameter: kwargs — line 154
# definition: test_invalid_authority_and_limits_fail_before_any_process — line 193
# parameter: fault — line 194
# parameter: monkeypatch — line 194
# parameter: native — line 194
# parameter: _args — line 200
# parameter: _kwargs — line 200
# variable: data — line 202
# variable: path — line 202
# variable: timeout — line 202
# variable: path — line 204
# variable: data — line 206
# variable: timeout — line 208
# definition: test_identity_failure_refuses_before_execution — line 218
# parameter: monkeypatch — line 218
# parameter: native — line 218
# parameter: _args — line 223
# variable: _ — line 223
# parameter: _args — line 228
# parameter: _kwargs — line 228
# definition: test_frozen_runner_dispatches_only_fixed_workers_and_validates_original_protocol — line 234
# parameter: monkeypatch — line 235
# parameter: native — line 235
# variable: observed — line 240
# definition: complete — line 242
# parameter: data — line 242
# parameter: path — line 242
# parameter: timeout — line 242
# definition: test_two_expired_drains_retain_owner_until_same_child_finishes — line 256
# parameter: monkeypatch — line 257
# parameter: native — line 257
# parameter: signal_error — line 257
# variable: _ — line 260
# variable: finished — line 260
# variable: pending — line 260
# variable: release — line 260
# variable: failures — line 261
# variable: observations — line 261
# definition: PendingProcess — line 263
# variable: returncode — line 266
# definition: communicate — line 268
# parameter: input — line 268
# parameter: self — line 268
# parameter: timeout — line 268
# attribute: returncode — line 278
# definition: poll — line 281
# parameter: self — line 281
# definition: kill — line 285
# parameter: self — line 285
# variable: process — line 290
# parameter: _args — line 292
# parameter: _kwargs — line 292
# definition: worker — line 295
# variable: thread — line 304
# variable: _ — line 317
# variable: timeout — line 317
# END CODE MAP

import subprocess
import threading

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


@pytest.mark.parametrize("signal_error", [False, True])
def test_two_expired_drains_retain_owner_until_same_child_finishes(
    native, monkeypatch, signal_error
):
    """A kill request cannot release the GUI worker/profile while the exact created child remains unreaped."""
    pending, release, finished = (threading.Event() for _ in range(3))
    observations, failures = [], []

    class PendingProcess:
        """Inert handle with two genuinely pending cleanup observations, never a discovered external PID."""

        returncode = None

        def communicate(self, *, input=None, timeout):
            """Hold final completion behind a gate while preserving the original analysis and drain deadlines."""
            observations.append((input, timeout))
            if len(observations) <= 3:
                raise subprocess.TimeoutExpired("owned-inert-parser", timeout)
            pending.set()
            if len(observations) == 4:
                raise OSError("first inert pending observation unavailable")
            if not release.wait(0.02):
                raise OSError("inert owned drain remains unavailable")
            self.returncode = -9
            return b"", None

        def poll(self):
            """No signal is exit evidence; the return code appears only after the gate releases the exact child."""
            return self.returncode

        def kill(self):
            """Unavailable signal delivery also cannot silently finish the owner."""
            if signal_error:
                raise OSError("inert kill unavailable")

    process = PendingProcess()
    monkeypatch.setattr(
        native_worker.subprocess, "Popen", lambda *_args, **_kwargs: process
    )

    def worker():
        """Returning would let the actual GUI release its workspace; capture the original analysis failure only after reap."""
        try:
            native_worker.run_owned(native, b"MSL1", 15)
        except BaseException as error:
            failures.append(error)
        finally:
            finished.set()

    thread = threading.Thread(target=worker)
    thread.start()
    try:
        assert pending.wait(3)
        assert thread.is_alive() and not finished.is_set() and failures == []
        assert process.poll() is None and native.is_file()
    finally:
        release.set()
        thread.join(3)
    assert not thread.is_alive() and process.poll() == -9
    assert len(failures) == 1 and isinstance(failures[0], subprocess.TimeoutExpired)
    assert failures[0].timeout == 15
    assert observations[:3] == [(b"MSL1", 15), (None, 5), (None, 5)]
    assert all(timeout == 1 for _, timeout in observations[3:])
