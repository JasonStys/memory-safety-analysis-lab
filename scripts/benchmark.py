"""Jason Stys: repeated release C++/Rust process-inclusive performance comparisons on identical data."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 29
# variable: result — line 31
# variable: count — line 43
# variable: data — line 44
# variable: inputs — line 45
# variable: expected — line 46
# variable: language — line 47
# variable: timings — line 49
# variable: _ — line 50
# variable: start — line 51
# variable: observed — line 52
# END CODE MAP

import json
import platform
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from msal.core import packet, reference
from msal.runner import ROOT, run


def main() -> None:
    """Warm both implementations and collect seven timings per size; correctness remains the hard gate."""
    result = {
        "schema": "msal-benchmark-v1",
        "author": "Jason Stys",
        "measured_at_utc": datetime.now(UTC).isoformat(),
        "os": platform.system(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "warmups": 1,
        "repeats": 7,
        "scope": "Release native startup + batch stdin/stdout + parsing/hash + Python metadata validation. No sanitizer/coverage instrumentation, generation or network. Not a pure parser benchmark or general language-speed claim.",
        "workloads": [],
    }
    for count in [1, 32, 128]:
        data = packet([(3, b"synthetic-data" * 8)] * count)
        inputs = [data] * 100
        expected = [reference(data)] * 100
        for language in ["cpp", "rust"]:
            assert run(language, inputs) == expected
            timings = []
            for _ in range(7):
                start = time.perf_counter()
                observed = run(language, inputs)
                timings.append(time.perf_counter() - start)
                assert observed == expected
            result["workloads"].append(
                {
                    "language": language,
                    "records_per_frame": count,
                    "frames": 100,
                    "frame_bytes": len(data),
                    "seconds": timings,
                    "median_seconds": statistics.median(timings),
                }
            )
    (ROOT / "out/benchmark.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
