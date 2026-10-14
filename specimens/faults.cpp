// Jason Stys: intentionally faulty synthetic sanitizer specimens; NEVER part of the default safe
// build. Execute only through the explicit Linux CI teaching harness; no arbitrary targets or
// exploit payloads.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// function occurrence: leak — line 37
// binding: value — line 38
// binding/parameter: value — line 38
// function occurrence: malloc — line 38
// binding/parameter: main — line 43
// function occurrence: main — line 43
// binding: index — line 45
// binding/parameter: index — line 45
// binding: value — line 46
// binding/parameter: value — line 46
// binding: index — line 49
// binding/parameter: index — line 49
// binding/parameter: value — line 50
// binding: value — line 53
// binding/parameter: value — line 53
// function occurrence: int — line 53
// binding: value — line 57
// binding/parameter: value — line 57
// function occurrence: int — line 57
// function occurrence: leak — line 62
// binding: value — line 65
// binding/parameter: value — line 65
// binding/parameter: eger — line 66
// END CODE MAP
#include <climits>
#include <cstdlib>
#if defined(__clang__)
#define MSAL_NOINLINE __attribute__((noinline))
#else
#define MSAL_NOINLINE
#endif
/// Lose ownership deliberately to verify LeakSanitizer, separate from all safe RAII code.
MSAL_NOINLINE void leak() {
  volatile auto *value = static_cast<int *>(std::malloc(32));
  if (value)
    value[0] = 42;
}
/// Each compile-time allowlisted case triggers exactly one known defect class.
int main() {
#if MSAL_CASE == 1
  volatile int index = 8;
  auto *value = new int[8]{};
  return value[index]; // EXPECTED: heap-buffer-overflow.
#elif MSAL_CASE == 2
  volatile int index = 8;
  int value[8]{};
  return value[index]; // EXPECTED: stack-buffer-overflow.
#elif MSAL_CASE == 3
  auto *value = new int(7);
  delete value;
  return *value; // EXPECTED: heap-use-after-free.
#elif MSAL_CASE == 4
  auto *value = new int(7);
  delete value;
  delete value; // EXPECTED: double-free.
  return 0;
#elif MSAL_CASE == 5
  leak(); // EXPECTED: detected memory leaks.
  return 0;
#elif MSAL_CASE == 6
  volatile int value = INT_MAX;
  return value + 1; // EXPECTED: signed integer overflow.
#else
#error "Select only a documented MSAL_CASE (1..6)"
#endif
}
