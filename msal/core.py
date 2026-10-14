"""Jason Stys: independent MSL1 reference decoder, deterministic corpus and strict native-result contract."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_BYTES — line 66
# variable: ERRORS — line 67
# definition: Outcome — line 85
# variable: status — line 88
# variable: code — line 89
# variable: count — line 90
# variable: bytes — line 91
# variable: fingerprint — line 92
# definition: reference — line 95
# parameter: data — line 95
# variable: count — line 103
# variable: cursor — line 106
# variable: fingerprint — line 106
# variable: payload_bytes — line 106
# variable: _ — line 107
# variable: length — line 110
# variable: tag — line 110
# variable: cursor — line 111
# variable: payload — line 118
# variable: value — line 122
# variable: value — line 125
# variable: fingerprint — line 126
# variable: payload_bytes — line 127
# variable: cursor — line 128
# definition: packet — line 134
# parameter: records — line 134
# variable: output — line 138
# variable: payload — line 139
# variable: tag — line 139
# variable: value — line 145
# variable: output — line 148
# definition: corpus — line 152
# variable: seed — line 154
# variable: cases — line 155
# variable: cases — line 168
# variable: index — line 168
# variable: state — line 169
# variable: index — line 170
# variable: state — line 171
# variable: changed — line 172
# definition: batch — line 178
# parameter: inputs — line 178
# variable: value — line 180
# variable: data — line 182
# variable: value — line 182
# definition: outcomes — line 188
# parameter: data — line 188
# parameter: expected_count — line 188
# variable: lines — line 192
# variable: result — line 195
# variable: line — line 196
# variable: fields — line 197
# variable: field — line 201
# variable: count — line 203
# variable: fingerprint — line 203
# variable: size — line 203
# END CODE MAP

from __future__ import annotations

import struct
from dataclasses import dataclass

MAX_BYTES = 1024 * 1024
ERRORS = frozenset(
    {
        "byte_limit",
        "header",
        "magic",
        "record_limit",
        "record_header",
        "tag",
        "payload_limit",
        "payload_truncated",
        "integer_width",
        "text",
        "trailing",
    }
)


@dataclass(frozen=True)
class Outcome:
    """Validated metadata only; hash is noncryptographic comparison data, not authentication."""

    status: str
    code: str = ""
    count: int = 0
    bytes: int = 0
    fingerprint: int = 0


def reference(data: bytes) -> Outcome:
    """Independently decode lengths with struct and own immutable slices; return stable errors."""
    if len(data) > MAX_BYTES:
        return Outcome("error", "byte_limit")
    if len(data) < 6:
        return Outcome("error", "header")
    if data[:4] != b"MSL1":
        return Outcome("error", "magic")
    count = struct.unpack_from("<H", data, 4)[0]
    if count > 128:
        return Outcome("error", "record_limit")
    cursor, payload_bytes, fingerprint = 6, 0, 14695981039346656037
    for _ in range(count):
        if len(data) - cursor < 3:
            return Outcome("error", "record_header")
        tag, length = struct.unpack_from("<BH", data, cursor)
        cursor += 3
        if not 1 <= tag <= 3:
            return Outcome("error", "tag")
        if length > 256:
            return Outcome("error", "payload_limit")
        if length > len(data) - cursor:
            return Outcome("error", "payload_truncated")
        payload = data[cursor : cursor + length]
        if tag == 1 and length != 4:
            return Outcome("error", "integer_width")
        if tag == 2 and (
            not payload or any(value < 32 or value > 126 for value in payload)
        ):
            return Outcome("error", "text")
        for value in bytes([tag]) + payload:
            fingerprint = ((fingerprint ^ value) * 1099511628211) & ((1 << 64) - 1)
        payload_bytes += length
        cursor += length
    if cursor != len(data):
        return Outcome("error", "trailing")
    return Outcome("ok", count=count, bytes=payload_bytes, fingerprint=fingerprint)


def packet(records: list[tuple[int, bytes]]) -> bytes:
    """Build only valid bounded synthetic records; callers cannot silently truncate lengths."""
    if len(records) > 128:
        raise ValueError("record limit")
    output = b"MSL1" + struct.pack("<H", len(records))
    for tag, payload in records:
        if type(tag) is not int or not 1 <= tag <= 3 or len(payload) > 256:
            raise ValueError("record field limit")
        if tag == 1 and len(payload) != 4:
            raise ValueError("integer width")
        if tag == 2 and (
            not payload or any(value < 32 or value > 126 for value in payload)
        ):
            raise ValueError("text range")
        output += struct.pack("<BH", tag, len(payload)) + payload
    return output


def corpus() -> list[tuple[str, bytes]]:
    """Include all reachable parser errors, valid tags, boundary records and truncated prefixes."""
    seed = packet([(1, b"\0\1\2\3"), (2, b"synthetic ~"), (3, b"\0\xff")])
    cases = [
        ("empty-record-set", packet([])),
        ("all-tags", seed),
        ("max-records", packet([(3, b"x" * 256)] * 128)),
        ("bad-magic", b"nope\0\0"),
        ("record-limit", b"MSL1\x81\0"),
        ("bad-tag", b"MSL1\1\0\0\0\0"),
        ("payload-limit", b"MSL1\1\0\3\1\1"),
        ("integer-width", b"MSL1\1\0\1\0\0"),
        ("empty-text", b"MSL1\1\0\2\0\0"),
        ("nonascii-text", b"MSL1\1\0\2\1\0\xff"),
        ("trailing", packet([]) + b"x"),
    ]
    cases += [(f"prefix-{index}", seed[:index]) for index in range(len(seed))]
    state = 0x5AB19C03
    for index in range(200):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        changed = bytearray(seed)
        changed[state % len(seed)] = (state >> 16) & 255
        cases.append((f"mutation-{index}", bytes(changed)))
    return cases


def batch(inputs: list[bytes]) -> bytes:
    """Encode ≤1000 data frames, ≤1 MiB each and ≤8 MiB total; inputs are never executable source."""
    if len(inputs) > 1000 or any(len(value) > MAX_BYTES for value in inputs):
        raise ValueError("batch frame/count limit")
    data = b"".join(struct.pack("<I", len(value)) + value for value in inputs)
    if len(data) > 8 * MAX_BYTES:
        raise ValueError("batch byte limit")
    return data


def outcomes(data: bytes, expected_count: int) -> list[Outcome]:
    """Validate exact native protocol, count, numeric ranges and safe allowlisted error codes."""
    if len(data) > 128 * 1024:
        raise ValueError("output byte limit")
    lines = data.decode("ascii").splitlines()
    if not lines or lines[0] != "MSAL\t1" or len(lines) != expected_count + 1:
        raise ValueError("output version/count")
    result = []
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) == 2 and fields[0] == "ERR" and fields[1] in ERRORS:
            result.append(Outcome("error", fields[1]))
        elif len(fields) == 4 and fields[0] == "OK":
            if not all(field.isascii() and field.isdecimal() for field in fields[1:]):
                raise ValueError("output integers")
            count, size, fingerprint = map(int, fields[1:])
            if (
                not 0 <= count <= 128
                or not 0 <= size <= count * 256
                or not 0 <= fingerprint < 1 << 64
            ):
                raise ValueError("output range")
            result.append(
                Outcome("ok", count=count, bytes=size, fingerprint=fingerprint)
            )
        else:
            raise ValueError("output row")
    return result
