cmake_minimum_required(VERSION 4.0)
project(project1_generate_me_a_project_team_name)

set(CMAKE_CXX_STANDARD 20)

include(FetchContent)

FetchContent_Declare(
        nlohmann_json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(nlohmann_json)

add_library(kvs_lib INTERFACE)


target_include_directories(kvs_lib INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(kvs_lib INTERFACE nlohmann_json::nlohmann_json)

add_executable(project1_generate_me_a_project_team_name main.cpp)

target_link_libraries(project1_generate_me_a_project_team_name PRIVATE kvs_lib)

enable_testing()

FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)

set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(run_tests tests/example_tests.cpp)

target_link_libraries(
        run_tests
        PRIVATE kvs_lib gtest_main
)

# Discover tests
include(GoogleTest)
gtest_discover_tests(run_tests)