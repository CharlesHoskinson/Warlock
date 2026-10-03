cmake_minimum_required(VERSION 3.20)
project(windowaccessibility LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_AUTOMOC ON)
find_package(Qt6 6.11 REQUIRED COMPONENTS Quick QuickPrivate Qml)
add_library(windowaccessibility MODULE bridge.cpp)
target_link_libraries(windowaccessibility PRIVATE Qt6::QuickPrivate Qt6::Qml)
set(WINDOW_ACCESSIBILITY_MODULE_DIR
    "/home/hoskinson/window-integration-qa/files-keyboard/guard-stage/WindowAccessibilityV5"
    CACHE PATH "Use a fresh module directory when an existing library is loaded")
set_target_properties(windowaccessibility PROPERTIES LIBRARY_OUTPUT_DIRECTORY
    "${WINDOW_ACCESSIBILITY_MODULE_DIR}")
