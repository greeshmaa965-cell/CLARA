# Parser and Semantic Analysis Progress

## Teammate 2 Responsibilities

Teammate 2 is responsible for:

- Abstract Syntax Tree (AST)
- Symbol table
- Parser and Bison grammar
- Semantic analysis
- Parser and semantic-analysis tests
- Parser and semantic-analysis documentation

---

## Phase 1: Interface Agreement

The parser and semantic-analysis work will use the token definitions provided by the lexer.

The current token categories include:

- Infrastructure keywords: `CLOUD`, `SERVER`, `DATABASE`, `CPU`, `MEMORY`, `STORAGE`, and `REGION`
- `IDENTIFIER`
- `NUMBER`
- `UNIT`
- `{` and `}`
- End of file
- Lexical error

The parser will eventually receive semantic values from the lexer, including:

- Identifier text
- Numeric values
- Unit text such as `MB`, `GB`, or `TB`

The lexer interface will be coordinated before parser integration.

---

## Phase 2: Abstract Syntax Tree

### Files Implemented

```text
include/ast/ast.h
src/ast/ast.c
tests/parser/ast_test.c