cmake_minimum_required(VERSION 3.22)

project(example VERSION 1.0)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Protobuf REQUIRED)

include_directories(
    ${PROTOBUF_INCLUDE_DIR}
    output/inc
)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)

add_executable(
    ${PROJECT_NAME}

    test.cpp
    output/src/bar.cpp
    output/src/bar.pb.cc
)

target_link_libraries(
    ${PROJECT_NAME}

    ${PROTOBUF_LIBRARY}
)