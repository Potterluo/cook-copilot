set(math_SOURCES
    math.cc
)

set(math_HEADERS
    math.hh
)

source_group("Header Files" FILES ${math_HEADERS})
source_group("Source Files" FILES ${math_SOURCES})

add_library(math ${math_SOURCES})