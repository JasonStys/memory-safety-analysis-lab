// Jason Stys: bounded binary batch stdin worker; safe parser metadata only, no arbitrary file
// execution.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// binding/parameter: main — line 42
// function occurrence: main — line 42
// binding: batch_limit — line 47
// binding/parameter: batch_limit — line 47
// parameter: std — line 48
// parameter: std — line 49
// function occurrence: read — line 51
// parameter: std — line 51
// binding: read — line 52
// binding/parameter: read — line 52
// function occurrence: gcount — line 52
// binding: index — line 55
// binding/parameter: index — line 55
// function occurrence: push_back — line 56
// binding: cursor — line 60
// binding/parameter: cursor — line 60
// parameter: std — line 60
// parameter: std — line 61
// binding: length — line 65
// parameter: std — line 65
// binding: shift — line 66
// binding/parameter: shift — line 66
// function occurrence: summary — line 72
// parameter: msal — line 72
// parameter: std — line 75
// binding/parameter: row — line 76
// parameter: std — line 77
// function occurrence: flush — line 78
// parameter: std — line 78
// END CODE MAP
#include "safe.hpp"
#include <array>
#include <iostream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
/// Read ≤8 MiB and ≤1000 explicit frames; reject a malformed batch before emitting any results.
int main() {
#ifdef _WIN32
  if (_setmode(_fileno(stdin), _O_BINARY) == -1)
    return 2;
#endif
  constexpr std::size_t batch_limit = 8 * msal::max_bytes;
  std::vector<std::uint8_t> data;
  std::array<char, 4096> block{};
  while (std::cin) {
    std::cin.read(block.data(), static_cast<std::streamsize>(block.size()));
    const auto read = static_cast<std::size_t>(std::cin.gcount());
    if (read > batch_limit - data.size())
      return 2;
    for (std::size_t index = 0; index < read; ++index)
      data.push_back(static_cast<std::uint8_t>(block[index]));
  }
  if (!std::cin.eof())
    return 2;
  std::size_t cursor = 0;
  std::vector<std::string> rows;
  while (cursor < data.size()) {
    if (rows.size() == 1000 || data.size() - cursor < 4)
      return 2;
    std::uint32_t length = 0;
    for (unsigned shift = 0; shift < 4; ++shift)
      length |= std::uint32_t{data[cursor + shift]} << (shift * 8);
    cursor += 4;
    if (length > msal::max_bytes || length > data.size() - cursor)
      return 2;
    rows.push_back(
        msal::summary(msal::parse(std::span<const std::uint8_t>(data).subspan(cursor, length))));
    cursor += length;
  }
  std::cout << "MSAL\t1\n";
  for (const auto &row : rows)
    std::cout << row << '\n';
  std::cout.flush();
  return std::cout ? 0 : 2;
}
