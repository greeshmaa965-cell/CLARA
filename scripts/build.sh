#!/usr/bin/env bash
set -e

echo "=== Building CLARA Compiler ==="

echo "[1/3] Generating lexer with Flex..."
flex -o src/lexer/lex.yy.c src/lexer/lexer.l

echo "[2/3] Compiling and running tests..."
gcc -Iinclude src/semantic/symbol_table.c tests/semantic/symbol_table_test.c -o tests/semantic/symbol_table_test
./tests/semantic/symbol_table_test
rm tests/semantic/symbol_table_test

gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c tests/semantic/semantic_test.c -o tests/semantic/semantic_test
./tests/semantic/semantic_test
rm tests/semantic/semantic_test

gcc -Iinclude src/ast/ast.c src/lexer/lex.yy.c src/parser/parser.c tests/parser/parser_test.c -o tests/parser/parser_test
./tests/parser/parser_test
rm tests/parser/parser_test

gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c src/lexer/lex.yy.c src/parser/parser.c src/ir/ir.c src/codegen/codegen.c tests/codegen/codegen_test.c -o tests/codegen/codegen_test
./tests/codegen/codegen_test
rm tests/codegen/codegen_test

echo "[3/3] Building clara executable..."
gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c src/lexer/lex.yy.c src/parser/parser.c src/ir/ir.c src/codegen/codegen.c src/main.c -o clara

rm src/lexer/lex.yy.c
echo "CLARA build complete! Run: ./clara --help"
