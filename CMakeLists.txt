cmake_minimum_required(VERSION 3.21)
project(NEXORA_Advanced C CXX)

include(CheckLanguage)
include(GNUInstallDirs)
find_package(Threads REQUIRED)

set(CMAKE_BUILD_TYPE Release)
set(BUILD_SHARED_LIBS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)

set(GGML_BUILD ON)
set(GGML_SHARED ON)
set(GGML_CPU ON)

add_compile_definitions(
    NDEBUG 
    GGML_VERSION="1.0.0" 
    GGML_COMMIT="nexora-latest"
)

set(GGML_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/ml/backend/ggml/ggml/src")

if(EXISTS "${GGML_SRC_DIR}")
    set(GGML_INCLUDE_DIRS
        ${GGML_SRC_DIR}
        ${GGML_SRC_DIR}/include
        ${GGML_SRC_DIR}/ggml-cpu
    )
    
    add_subdirectory(${GGML_SRC_DIR})
    
    if(TARGET ggml-base)
        target_include_directories(ggml-base PRIVATE ${GGML_INCLUDE_DIRS})
    endif()

    # تفعيل واجهة التسريع الرسومي Vulkan لتعزيز الأداء
    find_package(Vulkan)
    if(Vulkan_FOUND AND EXISTS "${GGML_SRC_DIR}/ggml-vulkan")
        add_subdirectory(${GGML_SRC_DIR}/ggml-vulkan)
        target_include_directories(ggml-vulkan PRIVATE ${GGML_INCLUDE_DIRS})
        message(STATUS "NEXORA: Vulkan backend enabled.")
    endif()
else()
    message(WARNING "GGML source directory not found at ${GGML_SRC_DIR}.")
endif()
