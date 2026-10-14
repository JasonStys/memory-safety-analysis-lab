// Jason Stys: libFuzzer callback exercises only safe bounded parser code under ASan/UBSan.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// binding/parameter: LLVMFuzzerTestOneInput — line 15
// binding/parameter: data — line 15
// binding/parameter: size — line 15
// function occurrence: LLVMFuzzerTestOneInput — line 15
// binding: parsed — line 17
// binding/parameter: parsed — line 17
// function occurrence: parse — line 17
// function occurrence: fingerprint — line 19
// END CODE MAP
#include "safe.hpp"
/// Arbitrary bytes are data, never code; exceptions are not swallowed and sanitizer crashes fail
/// CI.
extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data, std::size_t size) {
  if (size <= msal::max_bytes) {
    const auto parsed = msal::parse(std::span<const std::uint8_t>(data, size));
    if (std::holds_alternative<std::vector<msal::Record>>(parsed)) {
      (void)msal::fingerprint(std::get<std::vector<msal::Record>>(parsed));
    }
  }
  return 0;
}
