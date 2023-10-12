cmake_minimum_required(VERSION 3.22)

project(serializers VERSION 1.0)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(
    ${PROJECT_NAME} 
    
    STATIC 
    
    ${CMAKE_CURRENT_LIST_DIR}/src/bar.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/bar.pb.cc
)

target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_LIST_DIR}/inc)
target_link_libraries(${PROJECT_NAME})