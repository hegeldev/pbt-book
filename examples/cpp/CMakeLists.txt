cmake_minimum_required(VERSION 3.14)
project(lru_example CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

FetchContent_Declare(
	googletest
	GIT_REPOSITORY https://github.com/google/googletest.git
	GIT_TAG v1.17.0
)
FetchContent_Declare(
	hegel
	GIT_REPOSITORY https://github.com/hegeldev/hegel-cpp.git
	GIT_TAG v0.3.9
)
FetchContent_MakeAvailable(googletest hegel)

enable_testing()

add_executable(lru_test lru_test.cpp)
target_link_libraries(lru_test PRIVATE hegel GTest::gtest GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(lru_test)
