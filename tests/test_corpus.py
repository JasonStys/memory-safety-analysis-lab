"""Jason Stys: bounded data corpus and independently controlled disagreement-oracle regressions."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: controlled — line 62
# parameter: inputs — line 62
# parameter: language — line 62
# parameter: timeout — line 62
# variable: d — line 67
# definition: test_confirmed_reduction_and_no_disagreement — line 71
# variable: reduced — line 74
# variable: result — line 74
# variable: result — line 82
# variable: unchanged — line 82
# variable: result — line 88
# variable: unchanged — line 88
# definition: test_unstable_outcomes_are_not_minimized — line 101
# variable: calls — line 103
# definition: unstable — line 105
# parameter: inputs — line 105
# parameter: language — line 105
# parameter: timeout — line 105
# variable: calls — line 108
# variable: data — line 112
# variable: result — line 112
# definition: test_bounds — line 126
# parameter: kwargs — line 126
# definition: test_corpus_actual_workers_privacy_and_cli — line 132
# parameter: tmp_path — line 132
# variable: a — line 134
# variable: b — line 135
# variable: result — line 138
# variable: paths — line 149
# variable: timeout — line 169
# definition: test_disagreement_review_global_budget — line 174
# parameter: tmp_path — line 174
# variable: a — line 176
# variable: b — line 176
# variable: fake — line 179
# variable: p — line 184
# variable: result — line 190
# variable: r — line 191
# definition: test_aggregate_size_output_links_and_elapsed_budget — line 197
# parameter: tmp_path — line 197
# variable: p — line 199
# parameter: self — line 204
# variable: data — line 209
# variable: result — line 209
# END CODE MAP

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from msal import corpus as manager
from msal.core import Outcome, packet, reference
from msal.runner import run


def controlled(language, inputs, timeout=15):
    """Model a valid but disagreeing owned worker response only in tests, not a runtime faulty mode."""
    assert 0 < timeout <= 15
    return [
        Outcome("ok") if language == "cpp" and b"X" in d else reference(d)
        for d in inputs
    ]


def test_confirmed_reduction_and_no_disagreement():
    """Only twice-reproduced same agreement partition is retained; deterministic deletion reaches the one-byte witness."""
    with patch.object(manager, "run", side_effect=controlled):
        reduced, result = manager.minimize(b"prefixXsuffix", 128, 10)
        assert reduced == b"X" and result["state"] == "LOCAL_CHUNK_MINIMUM"
        assert result["retained_bytes"] == 1 and result["agreement_signature"] == (
            False,
            True,
            False,
        )
        assert manager.minimize(b"prefixXsuffix", 128, 10) == (reduced, result)
        unchanged, result = manager.minimize(b"no disagreement")
        assert (
            unchanged == b"no disagreement"
            and result["state"] == "NO_DISAGREEMENT"
            and result["attempts"] == 1
        )
        unchanged, result = manager.minimize(b"Xsuffix", 1)
        assert unchanged == b"Xsuffix" and result["state"] == "BUDGET_EXHAUSTED"
    with (
        patch.object(manager, "run", side_effect=ValueError("worker failure")),
        pytest.raises(ValueError),
    ):
        manager.minimize(b"X")
    with patch.object(
        manager, "run", side_effect=subprocess.TimeoutExpired("owned", 1)
    ):
        assert manager.minimize(b"X")[1]["state"] == "BUDGET_EXHAUSTED"


def test_unstable_outcomes_are_not_minimized():
    """A first disagreement that disappears on reproduction is explicitly inconclusive."""
    calls = 0

    def unstable(language, inputs, timeout):
        """First CPP response differs, subsequent validated results agree."""
        nonlocal calls
        calls += 1
        return [Outcome("ok") if calls == 1 else reference(inputs[0])]

    with patch.object(manager, "run", side_effect=unstable):
        data, result = manager.minimize(b"Xtail")
        assert data == b"Xtail" and result["state"] == "UNSTABLE_ORACLE"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"max_attempts": True},
        {"max_attempts": 129},
        {"seconds": 0},
        {"seconds": 31},
    ],
)
def test_bounds(kwargs):
    """Unbounded/coerced budgets fail before any workers launch."""
    with pytest.raises(ValueError):
        manager.minimize(b"x", **kwargs)


def test_corpus_actual_workers_privacy_and_cli(tmp_path: Path):
    """Actual fixed workers process unique hashes; original paths/payloads stay out of reports and existing output is preserved."""
    a = tmp_path / "private-payload.bin"
    b = tmp_path / "copy.bin"
    a.write_bytes(packet([(2, b"fictional-private-value")]))
    b.write_bytes(a.read_bytes())
    result = manager.review([b, a], tmp_path / "review", True)
    assert (
        result["case_count"] == 1
        and result["duplicate_files"] == 1
        and result["passed"]
    )
    assert "private-payload" not in json.dumps(
        result
    ) and "fictional-private" not in json.dumps(result)
    with pytest.raises(FileExistsError):
        manager.review([a], tmp_path / "review")
    for paths in ([], [a] * 1001):
        with pytest.raises(ValueError):
            manager.review(paths, tmp_path / "bad")
    with pytest.raises(ValueError):
        manager.review([a], tmp_path / "bad", max_attempts=0)
    with patch.object(Path, "is_symlink", return_value=True), pytest.raises(ValueError):
        manager.review([a], tmp_path / "linked")
    with patch.object(Path, "is_junction", side_effect=lambda: False):
        with patch.object(
            sys,
            "argv",
            ["corpus", "--input", str(a), "--output", str(tmp_path / "cli")],
        ):
            assert manager.main() == 0
        with patch.object(
            sys,
            "argv",
            ["corpus", "--input", str(a), "--output", str(tmp_path / "cli")],
        ):
            assert manager.main() == 2
    for timeout in (True, 0, 16, float("nan")):
        with pytest.raises(ValueError):
            run("cpp", [b"x"], timeout=timeout)


def test_disagreement_review_global_budget(tmp_path: Path):
    """One shared attempt budget prevents per-file multiplication; unattempted cases remain visible."""
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"Xa")
    b.write_bytes(b"Xb")
    fake = {"cases": [], "case_count": 2, "passed": False}
    import hashlib

    fake["cases"] = [
        {"case": hashlib.sha256(p.read_bytes()).hexdigest(), "matches": False}
        for p in (a, b)
    ]
    with (
        patch.object(manager, "compare", return_value=fake),
        patch.object(manager, "run", side_effect=controlled),
    ):
        result = manager.review([a, b], tmp_path / "reduction", True, 1)
    assert [r["state"] for r in result["reductions"]] == [
        "BUDGET_EXHAUSTED",
        "NOT_ATTEMPTED_BUDGET",
    ]


def test_aggregate_size_output_links_and_elapsed_budget(tmp_path: Path):
    """Aggregate submitted bytes are capped before corpus retention; late work cannot launch a worker."""
    p = tmp_path / "large"
    p.write_bytes(b"x" * 1_048_576)
    with pytest.raises(ValueError, match="byte cap"):
        manager.review([p] * 9, tmp_path / "large-review")
    with (
        patch.object(Path, "is_junction", lambda self: self.name == "linked-output"),
        pytest.raises(ValueError, match="output"),
    ):
        manager.review([p], tmp_path / "linked-output")
    with patch.object(manager.time, "monotonic", side_effect=[0, 100]):
        data, result = manager.minimize(b"X")
        assert (
            data == b"X"
            and result["state"] == "BUDGET_EXHAUSTED"
            and result["attempts"] == 0
        )
