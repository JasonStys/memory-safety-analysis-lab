"""Actual final portable widgets/core/native-window acceptance with independent oracles. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 122
# parameter: target — line 122
# parameter: window — line 122
# variable: load — line 128
# variable: gdi — line 129
# variable: user — line 129
# variable: pointer — line 130
# variable: arguments — line 131
# variable: library — line 131
# variable: name — line 131
# variable: result — line 131
# variable: function — line 157
# attribute: argtypes — line 158
# attribute: restype — line 158
# variable: handle — line 161
# variable: rectangle — line 162
# variable: height — line 165
# variable: width — line 165
# variable: source — line 168
# variable: destination — line 169
# variable: bitmap — line 170
# variable: previous — line 171
# variable: pixels — line 176
# variable: header — line 177
# variable: raw — line 195
# variable: scanlines — line 196
# variable: row — line 197
# variable: column — line 199
# variable: offset — line 200
# definition: chunk — line 203
# parameter: data — line 203
# parameter: name — line 203
# definition: oracle — line 225
# parameter: files — line 225
# parameter: index — line 225
# variable: result — line 227
# variable: row — line 233
# variable: row — line 245
# variable: expected — line 247
# variable: language — line 257
# variable: value — line 258
# definition: exercise — line 267
# parameter: output — line 267
# parameter: reopen — line 267
# parameter: window — line 267
# variable: expected — line 272
# variable: started — line 272
# variable: receipt — line 273
# variable: deadline — line 290
# definition: progress — line 292
# parameter: stage — line 292
# definition: finish — line 299
# parameter: failed — line 299
# attribute: acceptance_result — line 301
# variable: name — line 309
# variable: raw — line 309
# variable: row — line 311
# definition: checked — line 316
# parameter: callback — line 316
# variable: trace — line 324
# variable: trace — line 332
# definition: callback_failed — line 335
# parameter: _traceback — line 336
# parameter: _value — line 336
# parameter: kind — line 336
# definition: wait — line 342
# parameter: callback — line 342
# definition: layout — line 352
# variable: widgets — line 357
# variable: name — line 358
# variable: widget — line 360
# definition: rejected — line 382
# definition: licenses — line 391
# variable: dialogs — line 394
# variable: child — line 396
# variable: dialog — line 400
# variable: pending — line 401
# variable: texts — line 402
# variable: widget — line 404
# variable: text — line 410
# variable: value — line 411
# definition: completed — line 415
# parameter: index — line 415
# variable: files — line 421
# variable: parent — line 444
# variable: target — line 450
# variable: path — line 451
# variable: selected — line 454
# definition: start — line 466
# parameter: index — line 466
# variable: valid — line 473
# variable: invalid — line 474
# definition: begin — line 488
# variable: identity — line 492
# attribute: report_callback_exception — line 508
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import sys
import time
import tkinter as tk
import zlib
from pathlib import Path
from tkinter import ttk
from typing import TYPE_CHECKING, Any

from msal import desktop_project as project
from msal.desktop_io import json_value

if TYPE_CHECKING:
    from msal.desktop import Workbench


def capture(window: Workbench, target: Path) -> None:
    """Capture only this owned synthetic Tk window via PrintWindow, never the user's whole desktop."""
    if sys.platform != "win32":
        raise OSError("native screenshot acceptance targets Windows")
    from ctypes import wintypes

    load = ctypes.WinDLL
    user, gdi = load("user32", use_last_error=True), load("gdi32", use_last_error=True)
    pointer = ctypes.c_void_p
    for library, name, arguments, result in [
        (user, "GetAncestor", [pointer, ctypes.c_uint], pointer),
        (user, "GetWindowDC", [pointer], pointer),
        (gdi, "CreateCompatibleDC", [pointer], pointer),
        (gdi, "CreateCompatibleBitmap", [pointer, ctypes.c_int, ctypes.c_int], pointer),
        (gdi, "SelectObject", [pointer, pointer], pointer),
        (gdi, "DeleteObject", [pointer], ctypes.c_int),
        (gdi, "DeleteDC", [pointer], ctypes.c_int),
        (user, "ReleaseDC", [pointer, pointer], ctypes.c_int),
        (user, "PrintWindow", [pointer, pointer, ctypes.c_uint], ctypes.c_int),
        (user, "GetWindowRect", [pointer, ctypes.POINTER(wintypes.RECT)], ctypes.c_int),
        (
            gdi,
            "GetDIBits",
            [
                pointer,
                pointer,
                ctypes.c_uint,
                ctypes.c_uint,
                pointer,
                pointer,
                ctypes.c_uint,
            ],
            ctypes.c_int,
        ),
    ]:
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    # Flush this owned native window's pending control messages before reading its pixels.
    window.root.update()
    handle = user.GetAncestor(window.root.winfo_id(), 2)
    rectangle = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rectangle)):
        raise OSError("owned window bounds unavailable")
    width, height = rectangle.right - rectangle.left, rectangle.bottom - rectangle.top
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise OSError("owned screenshot outside bounded dimensions")
    source = user.GetWindowDC(handle)
    destination = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(destination, bitmap)
    try:
        if not user.PrintWindow(handle, destination, 2):
            raise OSError("owned window rendering unavailable")
        gdi.SelectObject(destination, previous)
        pixels = ctypes.create_string_buffer(width * height * 4)
        header = ctypes.create_string_buffer(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                width,
                -height,
                1,
                32,
                0,
                width * height * 4,
                0,
                0,
                0,
                0,
            )
        )
        if gdi.GetDIBits(source, bitmap, 0, height, pixels, header, 0) != height:
            raise OSError("owned screenshot pixels incomplete")
        raw = pixels.raw
        scanlines = bytearray()
        for row in range(height):
            scanlines.append(0)
            for column in range(width):
                offset = (row * width + column) * 4
                scanlines.extend((raw[offset + 2], raw[offset + 1], raw[offset]))

        def chunk(name: bytes, data: bytes) -> bytes:
            """Encode a bounded standard PNG chunk with its actual CRC."""
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data))
            )

        target.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
            + chunk(b"IEND", b"")
        )
    finally:
        gdi.SelectObject(destination, previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(destination)
        user.ReleaseDC(handle, source)


def oracle(index: int, files: dict[str, bytes]) -> None:
    """Independently require original corpus count, exact safe parser boundaries and duplicate accounting."""
    result = json_value(
        files["report.json"] if "report.json" in files else files["corpus.json"]
    )
    assert result["passed"] is True
    assert all(
        row["matches"] and row["expected"] == row["cpp"] == row["rust"]
        for row in result["cases"]
    )
    assert "universal memory safety" in json_value(files["input-scope.json"])["scope"]
    if index == 0:
        assert result["case_count"] == 243 and len(result["cases"]) == 243
    elif index == 8:
        assert (
            result["submitted_files"],
            result["duplicate_files"],
            result["case_count"],
        ) == (3, 1, 2)
        assert result["reductions"] == []
        assert {row["expected"]["status"] for row in result["cases"]} == {"ok", "error"}
    else:
        expected = {
            1: ("ok", "", 3, 23),
            2: ("error", "payload_truncated", 0, 0),
            3: ("error", "tag", 0, 0),
            4: ("ok", "", 128, 32768),
            5: ("error", "text", 0, 0),
            6: ("error", "trailing", 0, 0),
            7: ("error", "header", 0, 0),
        }
        assert result["case_count"] == 1
        for language in ("expected", "cpp", "rust"):
            value = result["cases"][0][language]
            assert (
                value["status"],
                value["code"],
                value["count"],
                value["bytes"],
            ) == expected[index]


def exercise(window: Workbench, output: Path, reopen: bool) -> None:
    """Drive the same real offline widgets/core worker and retained-owner close; supply only OS file-picker selection."""
    from unittest.mock import patch

    output.mkdir(mode=0o700)
    started, expected = time.monotonic(), 9
    receipt: dict[str, Any] = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": project.VERSION,
        "source": window.identity["source"],
        "source_dirty": window.identity["source_dirty"],
        "python_version": sys.version.split()[0],
        "python_dll_sha256": window.identity.get("python_dll_sha256"),
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "synthetic": True,
        "reopen": reopen,
        "passed": False,
        "steps": [],
        "tcl_version": str(window.root.tk.call("info", "patchlevel")),
        "tk_version": str(window.root.tk.call("package", "require", "Tk")),
    }
    deadline = started + 65

    def progress(stage: str) -> None:
        """Keep value-free milestone evidence if a native service or UI step fails."""
        receipt["last_stage"] = stage
        (output / "acceptance.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def finish(failed: bool = False) -> None:
        """Request normal close and preserve exact bundle identities; failure is never replaced by success on cleanup."""
        window.acceptance_result = not failed
        receipt["passed"] = not failed
        if failed:
            receipt["safe_application_status"] = window.status.get()[:240]
        receipt["journey_elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
        receipt["bundles"] = {
            str(row["id"]): {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in window.state.files(row["id"]).items()
            }
            for row in window.state.history()
        }
        progress("failed-retained" if failed else "normal-close-requested")
        window.exit()

    def checked(callback: Any) -> None:
        """A failed assertion becomes a nonzero normal app exit, without private exception/body output."""
        try:
            callback()
        except Exception as error:
            receipt["failure_stage"] = callback.__name__
            receipt["failure_type"] = type(error).__name__[:60]
            receipt["failure_step"] = receipt.get("last_stage")
            trace = error.__traceback__
            while trace is not None:
                if (
                    Path(trace.tb_frame.f_code.co_filename).name
                    == "native_acceptance.py"
                ):
                    receipt["failure_function"] = trace.tb_frame.f_code.co_name[:60]
                    receipt["failure_line"] = trace.tb_lineno
                trace = trace.tb_next
            finish(True)

    def callback_failed(
        kind: type[BaseException], _value: BaseException, _traceback: Any
    ) -> None:
        """Do not lose Tk callback errors in a windowed executable without stderr."""
        receipt["failure_type"] = kind.__name__[:60]
        finish(True)

    def wait(callback: Any) -> None:
        """Wait for the actual retained worker with one fixed deadline; no audit repetition or forced child abandonment."""
        if time.monotonic() > deadline:
            receipt["failure_stage"] = "owned-workflow-deadline"
            finish(True)
        elif window.busy:
            window.root.after(60, lambda: wait(callback))
        else:
            checked(callback)

    def layout() -> None:
        """Require real active controls and Exit to fit the minimum supported native window."""
        window.root.geometry("980x700")
        window.tabs.tk.call(str(window.tabs), "select", str(window.inputs_page))
        window.root.update()
        widgets: list[ttk.Widget] = [window.run_button, *window.footer_buttons.values()]
        for name in project.ACTIVE_FIELDS[window.mode.get()]:
            widgets.extend(window.field_widgets[name])
        for widget in widgets:
            assert widget.winfo_ismapped()
            assert (
                widget.winfo_rootx() >= window.root.winfo_rootx()
                and widget.winfo_rooty() >= window.root.winfo_rooty()
            )
            assert (
                widget.winfo_rootx() + widget.winfo_width()
                <= window.root.winfo_rootx() + window.root.winfo_width()
            )
            assert (
                widget.winfo_rooty() + widget.winfo_height()
                <= window.root.winfo_rooty() + window.root.winfo_height()
            )
        receipt["minimum_layout"] = {
            "width": 980,
            "height": 700,
            "activeInputsRunAndLifecycleVisible": True,
        }
        window.root.geometry("1260x860")
        window.root.update()

    def rejected() -> None:
        """A duplicate-key selected input must preserve every earlier real result and produce a visible rejection."""
        assert (
            len(window.state.history()) == expected
            and "rejected" in window.status.get().lower()
        )
        receipt["steps"].append("actual-invalid-input-retains-all-bundles")
        finish()

    def licenses() -> None:
        """Inspect the actual bundled text notice window, not a source-only declaration that licenses exist."""
        window.licenses()
        dialogs = [
            child
            for child in window.root.winfo_children()
            if isinstance(child, tk.Toplevel)
        ]
        assert len(dialogs) == 1
        dialog = dialogs[0]
        pending: list[tk.Misc] = [dialog]
        texts: list[tk.Text] = []
        while pending:
            widget = pending.pop()
            if isinstance(widget, tk.Text):
                texts.append(widget)
            pending.extend(widget.winfo_children())
            assert len(pending) < 1000
        assert len(texts) == 1
        text = texts[0].get("1.0", "end")
        assert all(value in text for value in ("Python", "Tcl", "Tk"))
        dialog.destroy()
        receipt["steps"].append("actual-bundled-runtime-license-window")

    def completed(index: int) -> None:
        """Read actual original outputs and inspect real rows; no service response or analysis result is mocked."""
        assert (
            len(window.state.history()) == index + 1
            and window.selected_run == index + 1
        )
        files = window.state.files(index + 1)
        oracle(index, files)
        if index in (0, 8):
            window.view.set("Three-way case outcomes")
            window.render()
            window.table.selection_set("0")
            window.inspect()
            assert json.loads(window.details.get("1.0", "end"))
            window.root.update()
            capture(
                window,
                output
                / (
                    "selected-evidence.png" if index < 8 else "owner-unknown-review.png"
                ),
            )
        receipt["steps"].append("actual-workflow-" + str(index + 1))
        if index + 1 < expected:
            start(index + 1)
        else:
            progress("runtime-license-window")
            licenses()
            progress("exact-export")
            parent = output / "exact-export"
            parent.mkdir()
            with patch(
                "msal.desktop.filedialog.askdirectory", return_value=str(parent)
            ):
                window.export_button.invoke()
            target = next(parent.iterdir())
            assert {path.name: path.read_bytes() for path in target.iterdir()} == files
            receipt["steps"].append("actual-exact-export")
            progress("invalid-report-retention")
            selected = output / "oversized-data.bin"
            selected.write_bytes(b"x" * (1024 * 1024 + 1))
            window.mode.set(project.MODES[1])
            with patch(
                "msal.desktop.filedialog.askopenfilenames",
                return_value=(str(selected),),
            ):
                window.choose("inputs", "files")
            window.authorized.set(True)
            window.run_button.invoke()
            wait(rejected)

    def start(index: int) -> None:
        """Prepared scenarios set ordinary controls; a real copied external report is selected through the same chooser."""
        progress("workflow-" + str(index + 1))
        window.prepared.set(project.SCENARIOS[index])
        window.load_prepared()
        assert not window.authorized.get()
        if index == 8:
            valid = output / "private-sample.bin"
            invalid = output / "truncated-sample.bin"
            valid.write_bytes(b"MSL1\x00\x00")
            invalid.write_bytes(b"MSL1")
            window.mode.set(project.MODES[1])
            with patch(
                "msal.desktop.filedialog.askopenfilenames",
                return_value=(str(valid), str(valid), str(invalid)),
            ):
                window.choose("inputs", "files")
        layout()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(lambda: completed(index))

    def begin() -> None:
        """A separate real process reopens all exact bundles without rerunning services or recomputing a prior report."""
        if reopen:
            assert len(window.state.history()) == expected
            for identity in range(1, expected + 1):
                window.history_table.selection_set(str(identity))
                window.open_button.invoke()
                assert window.selected_run == identity
                oracle(identity - 1, window.state.files(identity))
            receipt["steps"].append("actual-process-reopen-all-exact-bundles")
            finish()
        else:
            assert not window.state.history()
            window.run_button.invoke()
            assert (
                not window.state.history()
                and "permission" in window.status.get().lower()
            )
            start(0)

    window.root.report_callback_exception = callback_failed
    checked(begin)
