# CLARA Compiler Build Script for Windows PowerShell
$ErrorActionPreference = "Stop"

Write-Host "=== Building CLARA Compiler ===" -ForegroundColor Cyan

# Set toolchain PATH for MSYS2 if available
if (Test-Path "C:\msys64\ucrt64\bin") {
    $env:PATH = "C:\msys64\ucrt64\bin;C:\msys64\usr\bin;$env:PATH"
}

# Generate Lexer
Write-Host "[1/3] Generating lexer with Flex..."
flex -o src/lexer/lex.yy.c src/lexer/lexer.l

# Compile Tests
Write-Host "[2/3] Compiling and running tests..."
gcc -Iinclude src/semantic/symbol_table.c tests/semantic/symbol_table_test.c -o tests/semantic/symbol_table_test.exe
.\tests\semantic\symbol_table_test.exe
Remove-Item tests/semantic/symbol_table_test.exe

gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c tests/semantic/semantic_test.c -o tests/semantic/semantic_test.exe
.\tests\semantic\semantic_test.exe
Remove-Item tests/semantic/semantic_test.exe

gcc -Iinclude src/ast/ast.c src/lexer/lex.yy.c src/parser/parser.c tests/parser/parser_test.c -o tests/parser/parser_test.exe
.\tests\parser\parser_test.exe
Remove-Item tests/parser/parser_test.exe

gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c src/lexer/lex.yy.c src/parser/parser.c src/ir/ir.c src/codegen/codegen.c tests/codegen/codegen_test.c -o tests/codegen/codegen_test.exe
.\tests\codegen\codegen_test.exe
Remove-Item tests/codegen/codegen_test.exe

# Compile CLARA Executable
Write-Host "[3/3] Building clara.exe..."
gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c src/lexer/lex.yy.c src/parser/parser.c src/ir/ir.c src/codegen/codegen.c src/main.c -o clara.exe

# Clean up generated lexer file
Remove-Item src/lexer/lex.yy.c

Write-Host "`nCLARA build complete! Run: .\clara.exe --help" -ForegroundColor Green
