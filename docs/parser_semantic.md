# Parser and Semantic Analysis Documentation

## Overview

The Parser and Semantic Analysis subsystems form the core validation engine of the CLARA compiler. They transform the token stream produced by the Lexical Analyzer into an Abstract Syntax Tree (AST), populate the Symbol Table to enforce scoping and uniqueness, and execute semantic checks to ensure valid cloud configurations.

---

## Phase 1: Interface Agreement & Token Mapping

The parser consumes tokens defined in [include/tokens.h](file:///c:/Users/simsi/Projects/CLARA-1/include/tokens.h):

| Token Category | Token Type | Semantic Value | Example |
|---|---|---|---|
| Cloud Keyword | `TOKEN_CLOUD` | Keyword string | `CLOUD` |
| Server Keyword | `TOKEN_SERVER` | Keyword string | `SERVER` |
| Database Keyword | `TOKEN_DATABASE` | Keyword string | `DATABASE` |
| Resource Keywords | `TOKEN_CPU`, `TOKEN_MEMORY`, `TOKEN_STORAGE`, `TOKEN_REGION` | Keyword string | `CPU`, `REGION` |
| Identifiers | `TOKEN_IDENTIFIER` | String text | `aws`, `web_server`, `ap-south-1` |
| Numerics | `TOKEN_NUMBER` | Integer number | `4`, `16`, `500` |
| Units | `TOKEN_UNIT` | Unit string | `MB`, `GB`, `TB` |
| Delimiters | `TOKEN_LBRACE`, `TOKEN_RBRACE` | Symbol | `{`, `}` |
| Control | `TOKEN_EOF`, `TOKEN_LEXICAL_ERROR` | State code | End of input / error |

---

## Phase 2: Abstract Syntax Tree (AST)

The AST represents the hierarchical syntactic structure of a CLARA cloud specification.

### Data Structures ([include/ast/ast.h](file:///c:/Users/simsi/Projects/CLARA-1/include/ast/ast.h))

- **`ASTNodeType`**:
  - `AST_PROGRAM`: Root container holding cloud environments.
  - `AST_CLOUD`: Cloud provider block (e.g., `AWS`, `Azure`, `GCP`).
  - `AST_SERVER`: Compute instance definition (e.g., `web_server`).
  - `AST_DATABASE`: Managed database definition (e.g., `main_db`).
  - `AST_REGION`: Deployment region identifier (e.g., `ap-south-1`).
  - `AST_CPU`: CPU core count allocation.
  - `AST_MEMORY`: Memory allocation with optional unit.
  - `AST_STORAGE`: Storage capacity allocation with optional unit.

- **`ASTNode`**:
  - `type`: Node category.
  - `name`: Identifier name (for named declarations like cloud, server, database, region).
  - `value`: Optional text value.
  - `unit`: Measurement unit (e.g., `"GB"`, `"TB"`).
  - `number`: Numeric value for quantity nodes.
  - `children`: Dynamic array of child `ASTNode*` pointers.
  - `child_count`, `child_capacity`: Dynamic array tracking.

### Core AST Functions ([src/ast/ast.c](file:///c:/Users/simsi/Projects/CLARA-1/src/ast/ast.c))

- `ast_create_node(ASTNodeType type)`: Allocates and initializes a basic AST node.
- `ast_create_named_node(ASTNodeType type, const char *name)`: Creates a named node with duplicated string.
- `ast_create_number_node(ASTNodeType type, long number)`: Creates an integer quantity node.
- `ast_create_quantity_node(ASTNodeType type, long number, const char *unit)`: Creates a quantity node with unit.
- `ast_add_child(ASTNode *parent, ASTNode *child)`: Dynamically resizes parent child list and appends child.
- `ast_free(ASTNode *node)`: Recursively frees node and all child subtrees.
- `ast_print(const ASTNode *node, int indentation)`: Formats and outputs the AST to stdout with tree indentation.

---

## Phase 3: Symbol Table

The symbol table manages identifiers declared in the specification to prevent duplicates and resolve cross-references.

### Data Structures ([include/semantic/symbol_table.h](file:///c:/Users/simsi/Projects/CLARA-1/include/semantic/symbol_table.h))

- **`SymbolKind`**:
  - `SYMBOL_CLOUD`
  - `SYMBOL_SERVER`
  - `SYMBOL_DATABASE`

- **`Symbol`**: Contains name and symbol kind.
- **`SymbolTable`**: Hash table with open addressing / linear probing, dynamic resizing, and load-factor management.

### Core Symbol Table Functions ([src/semantic/symbol_table.c](file:///c:/Users/simsi/Projects/CLARA-1/src/semantic/symbol_table.c))

- `symbol_table_create(size_t capacity)`: Allocates hash table with given capacity (default 32).
- `symbol_table_destroy(SymbolTable *table)`: Frees table and stored symbol names.
- `symbol_table_insert(SymbolTable *table, const char *name, SymbolKind kind)`: Inserts a new symbol. Returns `false` on duplicate.
- `symbol_table_lookup(const SymbolTable *table, const char *name)`: Retrieves symbol pointer or `NULL` if not found.
- `symbol_table_contains(const SymbolTable *table, const char *name)`: Returns boolean existence check.

---

## Phase 4: Semantic Analysis & Diagnostics

The semantic analyzer verifies logical correctness and configuration constraints beyond syntax.

### Context & Interface ([include/semantic/semantic.h](file:///c:/Users/simsi/Projects/CLARA-1/include/semantic/semantic.h))

- `semantic_create(void)`: Initializes analyzer context with a fresh symbol table.
- `semantic_destroy(SemanticContext *context)`: Frees context and symbol table.
- `semantic_analyze(SemanticContext *context, const ASTNode *root)`: Traverses AST and validates semantic constraints.
- `semantic_error_count(const SemanticContext *context)`: Returns number of detected semantic errors.

### Semantic Rules Enforced ([src/semantic/semantic.c](file:///c:/Users/simsi/Projects/CLARA-1/src/semantic/semantic.c))

1. **Unique Declaration Rule**: Every cloud, server, and database declaration must have a unique identifier across the environment.
2. **Containment Rule**: `SERVER` and `DATABASE` components must be declared within a parent `CLOUD` block.
3. **Resource Bound Rule**: All CPU, MEMORY, and STORAGE values must be strictly greater than zero (`> 0`).
4. **Unit Specification Rule**: Memory and storage allocations require an explicit unit (e.g., `MB`, `GB`, `TB`).
5. **Non-Empty Name Rule**: All resource declarations must specify a non-empty name string.

---

## Phase 5: Parser Integration

The Parser integrates with the Lexer and AST to construct the syntax tree directly from source input:

```text
Source Text (.clara)
        ↓
Lexer (yylex) -> Token Stream
        ↓
Parser (clara_parse) -> Builds ASTNode Tree
        ↓
Semantic Analyzer (semantic_analyze) -> Symbol Table & Rule Verification
        ↓
Validated AST -> IR Generation
```

### Verified Tests

- `tests/semantic/symbol_table_test.c`: Validates insertion, duplicate rejection, and lookup.
- `tests/semantic/semantic_test.c`: Validates semantic analyzer against both valid and invalid AST structures.