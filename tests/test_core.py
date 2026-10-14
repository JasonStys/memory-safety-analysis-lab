"""Jason Stys: reference/native protocol bounds, deterministic corpus and malformed-data properties."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_exact_error — line 65
# parameter: code — line 65
# parameter: data — line 65
# definition: test_three_way_corpus — line 70
# variable: value — line 72
# variable: row — line 74
# definition: test_packet_rejects — line 89
# parameter: records — line 89
# definition: test_batch_limits — line 95
# definition: test_output_rejects — line 121
# parameter: count — line 121
# parameter: value — line 121
# definition: test_output_valid — line 127
# definition: test_arbitrary_data_agreement — line 140
# parameter: data — line 140
# variable: expected — line 142
# definition: test_raw_frame_transport — line 146
# variable: data — line 148
# variable: encoded — line 149
# END CODE MAP

import struct

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from msal.core import MAX_BYTES, Outcome, batch, corpus, outcomes, packet, reference
from msal.runner import compare, run


@pytest.mark.parametrize(
    "data,code",
    [
        (b"", "header"),
        (b"x" * (MAX_BYTES + 1), "byte_limit"),
        (b"xxxx\0\0", "magic"),
        (b"MSL1\x81\0", "record_limit"),
        (b"MSL1\1\0", "record_header"),
        (b"MSL1\1\0\0\0\0", "tag"),
        (b"MSL1\1\0\3\1\1", "payload_limit"),
        (b"MSL1\1\0\3\1\0", "payload_truncated"),
        (b"MSL1\1\0\1\0\0", "integer_width"),
        (b"MSL1\1\0\2\0\0", "text"),
        (b"MSL1\1\0\2\1\0\xff", "text"),
        (b"MSL1\0\0x", "trailing"),
    ],
    ids=[
        "header",
        "byte-limit",
        "magic",
        "record-limit",
        "record-header",
        "tag",
        "payload-limit",
        "truncated",
        "integer-width",
        "empty-text",
        "nonascii-text",
        "trailing",
    ],
)
def test_exact_error(data, code):
    """Every supported error is distinct; oversized packets are rejected by direct library contracts."""
    assert reference(data) == Outcome("error", code)


def test_three_way_corpus():
    """Execute the real C++ and Rust workers over every labeled case; no success mocks."""
    value = compare(corpus())
    assert value["passed"] and value["case_count"] == 243
    assert {row["expected"]["status"] for row in value["cases"]} == {"ok", "error"}


@pytest.mark.parametrize(
    "records",
    [
        [(3, b"")] * 129,
        [(4, b"")],
        [(True, b"")],
        [(3, b"x" * 257)],
        [(1, b"")],
        [(2, b"")],
        [(2, b"\xff")],
    ],
)
def test_packet_rejects(records):
    """The synthetic generator refuses malformed valid-record requests rather than truncating values."""
    with pytest.raises(ValueError):
        packet(records)


def test_batch_limits():
    """All batch cardinality, individual and aggregate byte caps are enforced before native execution."""
    assert batch([]) == b""
    with pytest.raises(ValueError):
        batch([b""] * 1001)
    with pytest.raises(ValueError):
        batch([b"x" * (MAX_BYTES + 1)])
    with pytest.raises(ValueError):
        batch([b"x" * MAX_BYTES] * 8)


@pytest.mark.parametrize(
    "value,count",
    [
        (b"", 0),
        (b"MSAL\t2\n", 0),
        (b"MSAL\t1\n", 1),
        (b"MSAL\t1\nERR\tunknown\n", 1),
        (b"MSAL\t1\nOK\t-1\t0\t0\n", 1),
        (b"MSAL\t1\nOK\t129\t0\t0\n", 1),
        (b"MSAL\t1\nOK\t0\t1\t0\n", 1),
        (b"MSAL\t1\nOK\t0\t0\t18446744073709551616\n", 1),
        (b"MSAL\t1\nOK\t1\t1\tx\n", 1),
        (b"MSAL\t1\n\xff\n", 1),
    ],
)
def test_output_rejects(value, count):
    """Output shape, ASCII numbers, cardinality and noncryptographic hash width are checked."""
    with pytest.raises(ValueError):
        outcomes(value, count)


def test_output_valid():
    """Both native row kinds and the empty batch are valid exact-schema outcomes."""
    assert outcomes(b"MSAL\t1\n", 0) == []
    assert outcomes(b"MSAL\t1\nOK\t0\t0\t14695981039346656037\nERR\theader\n", 2) == [
        reference(packet([])),
        Outcome("error", "header"),
    ]
    with pytest.raises(ValueError):
        outcomes(b"x" * (128 * 1024 + 1), 0)


@given(st.binary(max_size=4096))
@settings(max_examples=200, deadline=None, derandomize=True)
def test_arbitrary_data_agreement(data):
    """Bounded arbitrary bytes must give the same validated error/metadata across all three languages."""
    expected = reference(data)
    assert run("cpp", [data]) == run("rust", [data]) == [expected]


def test_raw_frame_transport():
    """Independent batch boundaries include NUL/newline/high bytes; text-mode pipes cannot corrupt data."""
    data = packet([(3, bytes(range(256)))])
    encoded = struct.pack("<I", len(data)) + data
    assert encoded == batch([data])
    assert run("cpp", [data]) == run("rust", [data]) == [reference(data)]
