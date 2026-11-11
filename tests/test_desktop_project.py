"""Real safe-worker data oracles, bounded private-corpus controls and payload-free evidence. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: execute — line 62
# parameter: parameters — line 62
# parameter: tmp_path — line 62
# variable: stage — line 64
# definition: test_original_243_cases_use_both_actual_workers_and_reference — line 69
# parameter: tmp_path — line 69
# variable: files — line 71
# variable: value — line 72
# variable: row — line 75
# variable: views — line 77
# variable: rows — line 80
# variable: row — line 81
# definition: test_prepared_binary_errors_and_boundaries_have_independent_oracles — line 97
# parameter: code — line 98
# parameter: count — line 98
# parameter: index — line 98
# parameter: size — line 98
# parameter: status — line 98
# parameter: tmp_path — line 98
# variable: files — line 101
# variable: value — line 102
# variable: row — line 105
# variable: language — line 106
# variable: outcome — line 107
# definition: test_selected_private_files_deduplicate_without_exporting_paths_or_payload — line 116
# parameter: tmp_path — line 117
# variable: one — line 120
# variable: bad — line 122
# variable: parameters — line 124
# variable: files — line 126
# variable: value — line 127
# variable: scope — line 134
# variable: raw — line 137
# definition: test_bad_parameters_refuse_without_payload_execution — line 157
# parameter: field — line 157
# parameter: tmp_path — line 157
# parameter: value — line 157
# variable: parameters — line 159
# definition: test_explicit_file_count_before_any_read — line 166
# parameter: paths — line 166
# parameter: tmp_path — line 166
# variable: parameters — line 168
# definition: test_input_and_aggregate_limits_preserve_original_sources — line 174
# parameter: tmp_path — line 174
# variable: large — line 176
# variable: parameters — line 178
# definition: test_legible_outcome_cells_preserve_complete_selected_evidence — line 188
# parameter: matches — line 188
# variable: expected — line 190
# variable: bad — line 191
# variable: row — line 192
# END CODE MAP

import pytest

from msal import desktop_project as project
from msal.desktop_io import Rejected, json_value


def execute(tmp_path, parameters):
    """Run the original compiled safe parsers; fixtures never supply executable/compiler paths."""
    stage = tmp_path / "stage"
    stage.mkdir()
    return project.analyze(None, parameters, stage)[2]


def test_original_243_cases_use_both_actual_workers_and_reference(tmp_path):
    """Preserve the original named denominator rather than silently deduplicating the teaching corpus."""
    files = execute(tmp_path, project.scenario(project.SCENARIOS[0]))
    value = json_value(files["report.json"])
    assert value["case_count"] == len(value["cases"]) == 243
    assert value["passed"] is True
    assert all(row["expected"] == row["cpp"] == row["rust"] for row in value["cases"])
    assert len(value["input_sha256"]) == 243
    views = project.views(files)
    assert len(views["Three-way case outcomes"]) == 243
    assert views["Disagreements only"] == []
    for rows in views.values():
        for row in rows:
            assert len(project.cells(row)) == 4


@pytest.mark.parametrize(
    "index,status,code,count,size",
    [
        (1, "ok", "", 3, 23),
        (2, "error", "payload_truncated", 0, 0),
        (3, "error", "tag", 0, 0),
        (4, "ok", "", 128, 32768),
        (5, "error", "text", 0, 0),
        (6, "error", "trailing", 0, 0),
        (7, "error", "header", 0, 0),
    ],
)
def test_prepared_binary_errors_and_boundaries_have_independent_oracles(
    tmp_path, index, status, code, count, size
):
    """Malformed data is a consistent parser rejection, not a worker crash, a vulnerability discovery or a failed test."""
    files = execute(tmp_path, project.scenario(project.SCENARIOS[index]))
    value = json_value(files["corpus.json"])
    assert value["case_count"] == value["submitted_files"] == 1
    assert value["passed"] is True
    row = value["cases"][0]
    for language in ("expected", "cpp", "rust"):
        outcome = row[language]
        assert (
            outcome["status"],
            outcome["code"],
            outcome["count"],
            outcome["bytes"],
        ) == (status, code, count, size)


def test_selected_private_files_deduplicate_without_exporting_paths_or_payload(
    tmp_path,
):
    """Actual supplied file bytes go through the original corpus engine; duplicate and invalid inputs remain in denominators."""
    one = tmp_path / "PRIVATE-INPUT-PATH.bin"
    one.write_bytes(b"MSL1\x00\x00")
    bad = tmp_path / "private-truncated.bin"
    bad.write_bytes(b"PRIVATE-PAYLOAD-MUST-NOT-LEAK")
    parameters = project.scenario(project.SCENARIOS[8])
    parameters.update(mode=project.MODES[1], inputs=f"{one}\n{one}\n{bad}")
    files = execute(tmp_path, parameters)
    value = json_value(files["corpus.json"])
    assert (
        value["submitted_files"],
        value["duplicate_files"],
        value["case_count"],
    ) == (3, 1, 2)
    assert value["passed"] is True and value["reductions"] == []
    scope = json_value(files["input-scope.json"])
    assert scope["reduction"] == "Reduce existing disagreements only"
    assert (scope["submitted_cases"], scope["evaluated_cases"]) == (3, 2)
    for raw in files.values():
        assert (
            b"PRIVATE-INPUT-PATH" not in raw
            and b"PRIVATE-PAYLOAD-MUST-NOT-LEAK" not in raw
        )
        assert str(tmp_path).encode() not in raw


@pytest.mark.parametrize(
    "field,value",
    [
        ("mode", "arbitrary-code"),
        ("max_attempts", "0"),
        ("max_attempts", "129"),
        ("max_attempts", "NaN"),
        ("max_attempts", "1.5"),
        ("reduction", "execute an arbitrary tool"),
        ("data_case", "foreign"),
    ],
)
def test_bad_parameters_refuse_without_payload_execution(tmp_path, field, value):
    """Invalid modes/budgets/choices never become defaults or a caller-selected execution path."""
    parameters = project.scenario(project.SCENARIOS[1])
    parameters[field] = value
    with pytest.raises((Rejected, ValueError)):
        execute(tmp_path, parameters)


@pytest.mark.parametrize("paths", ["", "\n".join(["not-opened"] * 1001)])
def test_explicit_file_count_before_any_read(tmp_path, paths):
    """Empty and excessive submissions fail before trying a possibly unrelated file."""
    parameters = project.scenario(project.SCENARIOS[1])
    parameters.update(mode=project.MODES[1], inputs=paths)
    with pytest.raises(Rejected, match="1 to 1000"):
        execute(tmp_path, parameters)


def test_input_and_aggregate_limits_preserve_original_sources(tmp_path):
    """The adapter bounds aggregate allocation during each stable read, not after collecting a possible gigabyte."""
    large = tmp_path / "large.bin"
    large.write_bytes(b"x" * (1024 * 1024))
    parameters = project.scenario(project.SCENARIOS[1])
    parameters.update(mode=project.MODES[1], inputs="\n".join([str(large)] * 8))
    with pytest.raises(Rejected, match="8 MiB"):
        execute(tmp_path, parameters)
    assert large.stat().st_size == 1024 * 1024
    with pytest.raises(Rejected):
        project.scenario("unknown")


@pytest.mark.parametrize("matches", [True, False])
def test_legible_outcome_cells_preserve_complete_selected_evidence(matches):
    """The grid exposes true counts/error differences while the unchanged selected row retains its complete identity."""
    expected = {"status": "ok", "count": 3, "bytes": 23, "fingerprint": 123, "code": ""}
    bad = {"status": "error", "count": 0, "bytes": 0, "fingerprint": 0, "code": "tag"}
    row = {
        "kind": "case",
        "case": "f" * 64,
        "expected": expected,
        "cpp": expected if matches else bad,
        "rust": expected,
        "matches": matches,
    }
    assert project.cells(row) == (
        "f" * 16 + "…",
        "OK 3r/23B",
        ("OK 3r/23B" if matches else "ERR tag") + " | OK 3r/23B",
        "AGREEMENT" if matches else "DISAGREEMENT",
    )
    assert row["case"] == "f" * 64 and row["expected"]["fingerprint"] == 123
