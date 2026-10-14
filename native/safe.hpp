// Jason Stys: bounds-checked owned record parsing and generation-safe handles; no raw owning
// pointers.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// binding/parameter: _view — line 62
// namespace: msal — line 66
// binding: max_bytes — line 67
// binding/parameter: max_bytes — line 67
// binding: max_records — line 68
// binding/parameter: max_records — line 68
// struct: Record — line 70
// binding/parameter: tag — line 71
// parameter: std — line 71
// parameter: std — line 72
// struct: Error — line 75
// binding/parameter: code — line 76
// parameter: std — line 76
// binding/parameter: count — line 80
// binding/parameter: limit — line 80
// binding/parameter: width — line 80
// function occurrence: extent — line 80
// parameter: std — line 80
// parameter: std — line 82
// binding/parameter: limit — line 83
// parameter: std — line 83
// function occurrence: parse — line 85
// binding/parameter: fingerprint — line 87
// function occurrence: fingerprint — line 87
// parameter: std — line 87
// binding/parameter: summary — line 89
// function occurrence: summary — line 89
// parameter: std — line 89
// struct: Handle — line 91
// binding/parameter: index — line 92
// parameter: std — line 92
// binding/parameter: generation — line 93
// parameter: std — line 93
// class: Arena — line 96
// struct: Slot — line 98
// binding: generation — line 99
// binding/parameter: generation — line 99
// parameter: std — line 99
// parameter: std — line 100
// parameter: std — line 102
// parameter: public — line 104
// binding/parameter: _view — line 106
// function occurrence: insert — line 106
// parameter: std — line 106
// binding/parameter: handle — line 108
// function occurrence: get — line 108
// parameter: std — line 108
// binding/parameter: erase — line 110
// binding/parameter: handle — line 110
// function occurrence: erase — line 110
// namespace: msal — line 112
// END CODE MAP
#pragma once
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

namespace msal {
inline constexpr std::size_t max_bytes = 1024 * 1024;
inline constexpr std::size_t max_records = 128;
/// A record owns its bytes; it cannot outlive a borrowed input view accidentally.
struct Record {
  std::uint8_t tag;
  std::vector<std::uint8_t> payload;
};
/// Stable application errors distinguish validation failure from a process/tool crash.
struct Error {
  std::string code;
};
using Parsed = std::variant<std::vector<Record>, Error>;
/// Validate count*width without performing an overflowing multiplication.
std::optional<std::size_t> extent(std::size_t count, std::size_t width, std::size_t limit);
/// Copy a non-owning input into an independently owned, bounded vector.
std::optional<std::vector<std::uint8_t>> copy(std::span<const std::uint8_t> input,
                                              std::size_t limit);
/// Parse complete MSL1 records; all lengths, tags, ASCII text and trailing bytes are validated.
Parsed parse(std::span<const std::uint8_t> input);
/// Return deterministic noncryptographic FNV-1a metadata, never authentication or payload content.
std::uint64_t fingerprint(const std::vector<Record> &records);
/// Format a safe parser result for cross-language comparison.
std::string summary(const Parsed &result);
/// A generation/index pair is a capability inside one arena, not a memory address.
struct Handle {
  std::size_t index;
  std::uint64_t generation;
};
/// Owned strings with stale/double-release detection; reads return copies, not dangling views.
class Arena {
  /// Each slot owns one value, or an empty reusable generation; generation zero is retired.
  struct Slot {
    std::uint64_t generation = 1;
    std::optional<std::string> value;
  };
  std::vector<Slot> slots_;

public:
  /// Insert ≤1024-byte text in ≤128 slots; reuse only nonretired generations.
  std::optional<Handle> insert(std::string_view value);
  /// Resolve only a live matching generation and copy its text for independent ownership.
  std::optional<std::string> get(Handle handle) const;
  /// Invalidate once; generation wrap retires a slot instead of reintroducing an old handle.
  bool erase(Handle handle);
};
} // namespace msal
