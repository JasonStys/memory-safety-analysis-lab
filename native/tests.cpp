// Jason Stys: always-active C++ bounds, ownership, stale-handle and malformed parser regressions.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// binding: checks — line 86
// binding/parameter: checks — line 86
// binding/parameter: value — line 88
// function occurrence: require — line 88
// function occurrence: runtime_error — line 91
// binding/parameter: tag — line 94
// function occurrence: record — line 94
// parameter: std — line 95
// function occurrence: insert — line 104
// binding/parameter: _view — line 108
// function occurrence: rejects — line 108
// binding: value — line 109
// binding/parameter: value — line 109
// function occurrence: parse — line 109
// function occurrence: require — line 110
// function occurrence: require — line 111
// binding/parameter: main — line 114
// function occurrence: main — line 114
// function occurrence: require — line 115
// function occurrence: require — line 116
// function occurrence: require — line 117
// function occurrence: require — line 118
// function occurrence: require — line 119
// parameter: std — line 120
// binding: owned — line 121
// binding/parameter: owned — line 121
// function occurrence: copy — line 121
// function occurrence: clear — line 122
// function occurrence: require — line 123
// function occurrence: require — line 124
// function occurrence: empty — line 125
// function occurrence: rejects — line 127
// function occurrence: rejects — line 132
// binding: truncated — line 133
// binding/parameter: truncated — line 133
// function occurrence: pop_back — line 134
// function occurrence: rejects — line 135
// binding/parameter: eger_width — line 136
// binding: trailing — line 140
// binding/parameter: trailing — line 140
// function occurrence: push_back — line 141
// function occurrence: rejects — line 142
// binding/parameter: data — line 143
// binding: parsed — line 144
// binding/parameter: parsed — line 144
// function occurrence: parse — line 144
// function occurrence: require — line 145
// function occurrence: require — line 146
// binding: empty — line 148
// binding/parameter: empty — line 148
// function occurrence: require — line 149
// parameter: msal — line 151
// function occurrence: require — line 154
// binding: source — line 155
// binding/parameter: source — line 155
// parameter: std — line 155
// binding: first — line 156
// binding/parameter: first — line 156
// function occurrence: insert — line 156
// function occurrence: clear — line 157
// binding: snapshot — line 158
// binding/parameter: snapshot — line 158
// function occurrence: get — line 158
// function occurrence: require — line 159
// function occurrence: require — line 160
// function occurrence: require — line 161
// binding: replacement — line 162
// binding/parameter: replacement — line 162
// function occurrence: insert — line 162
// function occurrence: require — line 163
// function occurrence: require — line 164
// function occurrence: require — line 165
// binding: index — line 166
// binding/parameter: index — line 166
// function occurrence: require — line 167
// function occurrence: require — line 168
// parameter: std — line 169
// END CODE MAP
#include "safe.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
/// Count assertions in Release too; NDEBUG must never disable these acceptance checks.
static std::size_t checks = 0;
/// Fail explicitly on a mismatched invariant; expression names contain no input payload.
static void require(bool value) {
  ++checks;
  if (!value)
    throw std::runtime_error("safe invariant failed");
}
/// Construct a single-record fixture independently of the Python encoder.
static std::vector<std::uint8_t> record(std::uint8_t tag, std::vector<std::uint8_t> payload) {
  std::vector<std::uint8_t> result{'M',
                                   'S',
                                   'L',
                                   '1',
                                   1,
                                   0,
                                   tag,
                                   static_cast<std::uint8_t>(payload.size() & 255),
                                   static_cast<std::uint8_t>(payload.size() >> 8)};
  result.insert(result.end(), payload.begin(), payload.end());
  return result;
}
/// Compare a stable parser rejection rather than merely checking a nonzero process exit.
static void rejects(const std::vector<std::uint8_t> &input, std::string_view expected) {
  const auto value = msal::parse(input);
  require(std::holds_alternative<msal::Error>(value));
  require(std::get<msal::Error>(value).code == expected);
}
/// Exercise every authored parser error and valid tag, boundary arithmetic and arena ownership.
int main() {
  require(msal::extent(0, 4, 16) == 0);
  require(msal::extent(4, 4, 16) == 16);
  require(!msal::extent(5, 4, 16));
  require(!msal::extent(1, 0, 16));
  require(!msal::extent(std::numeric_limits<std::size_t>::max(), 2, 1024));
  std::vector<std::uint8_t> bytes{1, 2, 3};
  auto owned = msal::copy(bytes, 3);
  bytes.clear();
  require(owned && owned->size() == 3);
  require(!msal::copy(*owned, 2));
  require(msal::copy({}, 0)->empty());
  rejects({}, "header");
  rejects(std::vector<std::uint8_t>(msal::max_bytes + 1), "byte_limit");
  rejects({0, 0, 0, 0, 0, 0}, "magic");
  rejects({'M', 'S', 'L', '1', 129, 0}, "record_limit");
  rejects({'M', 'S', 'L', '1', 1, 0}, "record_header");
  rejects(record(0, {}), "tag");
  rejects(record(3, std::vector<std::uint8_t>(257)), "payload_limit");
  auto truncated = record(3, {1, 2});
  truncated.pop_back();
  rejects(truncated, "payload_truncated");
  rejects(record(1, {}), "integer_width");
  rejects(record(2, {}), "text");
  rejects(record(2, {0}), "text");
  rejects(record(2, {127}), "text");
  auto trailing = record(3, {});
  trailing.push_back(0);
  rejects(trailing, "trailing");
  for (const auto &data : {record(1, {0, 1, 2, 3}), record(2, {' ', '~'}), record(3, {})}) {
    const auto parsed = msal::parse(data);
    require(std::holds_alternative<std::vector<msal::Record>>(parsed));
    require(msal::summary(parsed).starts_with("OK\t1\t"));
  }
  const auto empty = msal::parse(std::vector<std::uint8_t>{'M', 'S', 'L', '1', 0, 0});
  require(msal::summary(empty) == "OK\t0\t0\t14695981039346656037");
  require(msal::summary(msal::Error{"text"}) == "ERR\ttext");
  msal::Arena arena;
  require(!arena.get({999, 1}));
  require(!arena.erase({999, 1}));
  require(!arena.insert(std::string(1025, 'x')));
  std::string source = "owned";
  const auto first = *arena.insert(source);
  source.clear();
  auto snapshot = *arena.get(first);
  require(arena.erase(first));
  require(!arena.get(first));
  require(!arena.erase(first));
  const auto replacement = *arena.insert("new");
  require(replacement.index == first.index && replacement.generation != first.generation);
  require(!arena.get(first) && !arena.erase(first));
  require(arena.get(replacement) == "new" && snapshot == "owned");
  for (std::size_t index = 1; index < msal::max_records; ++index)
    require(arena.insert("").has_value());
  require(!arena.insert("full"));
  std::cout << "C++ safe invariant assertions: " << checks << " passed\n";
}
