// Jason Stys: safe C++20 parsing/ownership fixes for bounds, length arithmetic and stale lifetimes.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// namespace: msal — line 89
// binding/parameter: count — line 91
// binding/parameter: limit — line 91
// binding/parameter: width — line 91
// function occurrence: extent — line 91
// parameter: std — line 91
// parameter: std — line 97
// binding/parameter: limit — line 98
// parameter: std — line 98
// function occurrence: begin — line 101
// binding/parameter: position — line 104
// binding/parameter: word — line 104
// function occurrence: word — line 104
// function occurrence: parse — line 108
// binding: count — line 115
// binding/parameter: count — line 115
// function occurrence: word — line 115
// parameter: std — line 118
// function occurrence: reserve — line 119
// binding: cursor — line 120
// binding/parameter: cursor — line 120
// parameter: std — line 120
// binding: index — line 121
// binding/parameter: index — line 121
// binding: tag — line 124
// binding/parameter: tag — line 124
// binding: length — line 125
// binding/parameter: length — line 125
// function occurrence: word — line 125
// binding: view — line 133
// binding/parameter: view — line 133
// function occurrence: subspan — line 133
// binding/parameter: eger_width — line 135
// binding/parameter: byte — line 136
// binding/parameter: fingerprint — line 148
// function occurrence: fingerprint — line 148
// parameter: std — line 148
// binding: hash — line 149
// binding/parameter: hash — line 149
// parameter: std — line 149
// binding/parameter: record — line 150
// binding: hash — line 151
// binding/parameter: byte — line 152
// binding: hash — line 153
// binding/parameter: summary — line 158
// function occurrence: summary — line 158
// parameter: std — line 158
// binding: error — line 159
// binding/parameter: error — line 159
// binding: records — line 161
// binding/parameter: records — line 161
// binding: bytes — line 162
// binding/parameter: bytes — line 162
// parameter: std — line 162
// binding/parameter: record — line 163
// function occurrence: size — line 164
// function occurrence: to_string — line 166
// parameter: std — line 166
// binding/parameter: _view — line 169
// function occurrence: insert — line 169
// parameter: std — line 169
// binding: index — line 172
// binding/parameter: index — line 172
// function occurrence: size — line 172
// binding: slot — line 173
// binding/parameter: slot — line 173
// binding: value — line 175
// function occurrence: string — line 175
// binding/parameter: handle — line 185
// function occurrence: get — line 185
// parameter: std — line 185
// binding: slot — line 188
// binding/parameter: slot — line 188
// binding/parameter: Arena — line 194
// binding/parameter: handle — line 194
// function occurrence: erase — line 194
// binding: slot — line 197
// binding/parameter: slot — line 197
// function occurrence: reset — line 200
// binding: generation — line 201
// namespace: msal — line 205
// END CODE MAP
#include "safe.hpp"
#include <algorithm>
#include <limits>

namespace msal {
/// Division guard bounds count and width before multiplication can overflow size_t.
std::optional<std::size_t> extent(std::size_t count, std::size_t width, std::size_t limit) {
  if (width == 0 || count > limit / width)
    return std::nullopt;
  return count * width;
}
/// The returned bytes own their storage, unlike a span into a short-lived source.
std::optional<std::vector<std::uint8_t>> copy(std::span<const std::uint8_t> input,
                                              std::size_t limit) {
  if (input.size() > limit)
    return std::nullopt;
  return std::vector<std::uint8_t>(input.begin(), input.end());
}
/// Only call after proving two bytes remain; widening happens before shifting.
static std::size_t word(std::span<const std::uint8_t> input, std::size_t position) {
  return std::size_t{input[position]} | (std::size_t{input[position + 1]} << 8);
}
/// Every cursor advance is guarded by remaining bytes; zero-length valid blobs are supported.
Parsed parse(std::span<const std::uint8_t> input) {
  if (input.size() > max_bytes)
    return Error{"byte_limit"};
  if (input.size() < 6)
    return Error{"header"};
  if (input[0] != 'M' || input[1] != 'S' || input[2] != 'L' || input[3] != '1')
    return Error{"magic"};
  const auto count = word(input, 4);
  if (count > max_records)
    return Error{"record_limit"};
  std::vector<Record> records;
  records.reserve(count);
  std::size_t cursor = 6;
  for (std::size_t index = 0; index < count; ++index) {
    if (input.size() - cursor < 3)
      return Error{"record_header"};
    const auto tag = input[cursor];
    const auto length = word(input, cursor + 1);
    cursor += 3;
    if (tag < 1 || tag > 3)
      return Error{"tag"};
    if (length > 256)
      return Error{"payload_limit"};
    if (length > input.size() - cursor)
      return Error{"payload_truncated"};
    const auto view = input.subspan(cursor, length);
    if (tag == 1 && length != 4)
      return Error{"integer_width"};
    if (tag == 2 && (length == 0 || !std::all_of(view.begin(), view.end(), [](auto byte) {
                       return byte >= 32 && byte <= 126;
                     })))
      return Error{"text"};
    records.push_back(Record{tag, *copy(view, 256)});
    cursor += length;
  }
  if (cursor != input.size())
    return Error{"trailing"};
  return records;
}
/// Unsigned wrap is intentional FNV arithmetic, not signed overflow or a security checksum.
std::uint64_t fingerprint(const std::vector<Record> &records) {
  std::uint64_t hash = 14695981039346656037ULL;
  for (const auto &record : records) {
    hash = (hash ^ record.tag) * 1099511628211ULL;
    for (auto byte : record.payload)
      hash = (hash ^ byte) * 1099511628211ULL;
  }
  return hash;
}
/// Only metadata and stable codes leave the parser; no input text or payload is logged.
std::string summary(const Parsed &result) {
  if (const auto *error = std::get_if<Error>(&result))
    return "ERR\t" + error->code;
  const auto &records = std::get<std::vector<Record>>(result);
  std::size_t bytes = 0;
  for (const auto &record : records)
    bytes += record.payload.size();
  return "OK\t" + std::to_string(records.size()) + "\t" + std::to_string(bytes) + "\t" +
         std::to_string(fingerprint(records));
}
/// Owning copies and RAII replace borrowed pointers; bounded reuse prevents indefinite allocations.
std::optional<Handle> Arena::insert(std::string_view value) {
  if (value.size() > 1024)
    return std::nullopt;
  for (std::size_t index = 0; index < slots_.size(); ++index) {
    auto &slot = slots_[index];
    if (!slot.value && slot.generation != 0) {
      slot.value = std::string(value);
      return Handle{index, slot.generation};
    }
  }
  if (slots_.size() == max_records)
    return std::nullopt;
  slots_.push_back(Slot{1, std::string(value)});
  return Handle{slots_.size() - 1, 1};
}
/// Never return a pointer/reference into a value that a later erase or reallocation can invalidate.
std::optional<std::string> Arena::get(Handle handle) const {
  if (handle.index >= slots_.size())
    return std::nullopt;
  const auto &slot = slots_[handle.index];
  if (slot.generation != handle.generation || !slot.value)
    return std::nullopt;
  return *slot.value;
}
/// Double release and stale generations are controlled failures, not undefined behavior.
bool Arena::erase(Handle handle) {
  if (handle.index >= slots_.size())
    return false;
  auto &slot = slots_[handle.index];
  if (slot.generation != handle.generation || !slot.value)
    return false;
  slot.value.reset();
  slot.generation =
      slot.generation == std::numeric_limits<std::uint64_t>::max() ? 0 : slot.generation + 1;
  return true;
}
} // namespace msal
