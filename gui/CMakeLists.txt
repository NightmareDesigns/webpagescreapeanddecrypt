cmake_minimum_required(VERSION 3.16)
project(WebScraperGUI VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Find Qt6 or Qt5
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Widgets)

set(PROJECT_SOURCES
    main.cpp
    mainwindow.cpp
    mainwindow.h
)

if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(WebScraperGUI
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
    )
else()
    add_executable(WebScraperGUI ${PROJECT_SOURCES})
endif()

target_link_libraries(WebScraperGUI PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

# Set output directory to repository root for easy access to scraper.py
set_target_properties(WebScraperGUI PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/.."
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_finalize_executable(WebScraperGUI)
endif()

# Install target
install(TARGETS WebScraperGUI
    RUNTIME DESTINATION bin
)
