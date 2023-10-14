cmake_minimum_required(VERSION 3.22)

project(serializers VERSION 1.0)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(${CMAKE_CURRENT_LIST_DIR})

add_library(
    ${PROJECT_NAME} 
    
    STATIC 
    
    src/bar.cpp
)