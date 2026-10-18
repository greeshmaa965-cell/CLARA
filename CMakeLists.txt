cmake_minimum_required(VERSION 3.15)

project(CLARA C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

include_directories(include)

find_package(FLEX REQUIRED)
FLEX_TARGET(CLARAScanner src/lexer/lexer.l ${CMAKE_CURRENT_BINARY_DIR}/lex.yy.c)

set(CLARA_CORE_SOURCES
    src/ast/ast.c
    src/semantic/symbol_table.c
    src/semantic/semantic.c
    src/parser/parser.c
    src/ir/ir.c
    src/codegen/codegen.c
    ${FLEX_CLARAScanner_OUTPUTS}
)

add_executable(clara
    src/main.c
    ${CLARA_CORE_SOURCES}
)

# Test executables
add_executable(symbol_table_test
    src/semantic/symbol_table.c
    tests/semantic/symbol_table_test.c
)

add_executable(semantic_test
    src/ast/ast.c
    src/semantic/symbol_table.c
    src/semantic/semantic.c
    tests/semantic/semantic_test.c
)

add_executable(parser_test
    src/ast/ast.c
    src/parser/parser.c
    ${FLEX_CLARAScanner_OUTPUTS}
    tests/parser/parser_test.c
)

add_executable(codegen_test
    src/ast/ast.c
    src/semantic/symbol_table.c
    src/semantic/semantic.c
    src/parser/parser.c
    src/ir/ir.c
    src/codegen/codegen.c
    ${FLEX_CLARAScanner_OUTPUTS}
    tests/codegen/codegen_test.c
)

enable_testing()
add_test(NAME SymbolTableTest COMMAND symbol_table_test)
add_test(NAME SemanticTest COMMAND semantic_test)
add_test(NAME ParserTest COMMAND parser_test)
add_test(NAME CodegenTest COMMAND codegen_test)