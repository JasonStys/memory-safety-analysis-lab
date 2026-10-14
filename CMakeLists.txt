# Jason Stys: default safe C++20 build; deliberately faulty specimens are never targets here.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# CMake command: cmake_minimum_required — line 30
# CMake command: project — line 31
# CMake command: set — line 32
# CMake command: set — line 33
# CMake command: set — line 34
# CMake command: option — line 35
# CMake command: option — line 36
# CMake command: add_library — line 37
# CMake command: target_include_directories — line 38
# CMake command: if — line 39
# CMake command: else — line 41
# CMake command: endif — line 43
# CMake command: if — line 44
# CMake command: endif — line 48
# CMake command: if — line 49
# CMake command: endif — line 52
# CMake command: if — line 53
# CMake command: endif — line 56
# CMake command: add_executable — line 57
# CMake command: target_link_libraries — line 58
# CMake command: add_executable — line 59
# CMake command: target_link_libraries — line 60
# CMake command: foreach — line 61
# CMake command: endforeach — line 67
# CMake command: enable_testing — line 68
# CMake command: add_test — line 69
# END CODE MAP
cmake_minimum_required(VERSION 3.24)
project(memory_safety_analysis_lab VERSION 1.0.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
option(MSAL_SANITIZE "Instrument SAFE targets with ASan/UBSan on Clang" OFF)
option(MSAL_COVERAGE "Instrument SAFE targets with Clang source coverage" OFF)
add_library(msal native/safe.cpp)
target_include_directories(msal PUBLIC native)
if(MSVC)
  target_compile_options(msal PRIVATE /W4 /WX /permissive-)
else()
  target_compile_options(msal PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Werror)
endif()
if(MSAL_SANITIZE OR MSAL_COVERAGE)
  if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    message(FATAL_ERROR "Instrumentation requires Clang")
  endif()
endif()
if(MSAL_SANITIZE)
  target_compile_options(msal PUBLIC -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer)
  target_link_options(msal PUBLIC -fsanitize=address,undefined -fno-sanitize-recover=all)
endif()
if(MSAL_COVERAGE)
  target_compile_options(msal PUBLIC -fprofile-instr-generate -fcoverage-mapping)
  target_link_options(msal PUBLIC -fprofile-instr-generate)
endif()
add_executable(parser-cpp native/main.cpp)
target_link_libraries(parser-cpp PRIVATE msal)
add_executable(test-cpp native/tests.cpp)
target_link_libraries(test-cpp PRIVATE msal)
foreach(target parser-cpp test-cpp)
  if(MSVC)
    target_compile_options(${target} PRIVATE /W4 /WX /permissive-)
  else()
    target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Werror)
  endif()
endforeach()
enable_testing()
add_test(NAME safe-native COMMAND test-cpp)
