# CLARA (Cloud Language, Analysis, and Resource Architecture)

> A compiler-based Domain-Specific Language (DSL) and intelligent recommendation engine for declarative, validated, and explainable cloud infrastructure.

---

## 📌 Overview

**CLARA** simplifies cloud resource modeling by providing a dedicated domain-specific language coupled with a robust compiler frontend (lexer, parser, AST, symbol table, semantic analyzer) and an intermediate representation (IR) backend.

Beyond standard infrastructure-as-code compilation, CLARA introduces three novelty capabilities:
1. **Dual-Mode Input Normalization**: Accepts both unstructured natural language and structured form inputs, converting both into a canonical JSON representation.
2. **Constraint-Aware Alternative Generation**: Evaluates multiple feasible cloud architectures and ranks them across cost, capacity, and performance trade-offs.
3. **Explainable Configuration Diff**: Generates transparent, field-level comparative diffs explaining *why* specific configuration adjustments are recommended.

---

## ⚙️ Architecture & Pipeline

```text
User Input: Natural Language or Form Input
                     ↓
         Canonical JSON Normalization
                     ↓
             CLARA DSL (.clara)
                     ↓
         Lexical Analysis (Flex)
                     ↓
         Parser & AST Construction
                     ↓
     Symbol Table & Semantic Validation
                     ↓
         Intermediate Representation (IR)
                     ↓
       Candidate Engine & Diff Explainer
                     ↓
      Target Code Generation (Terraform / JSON)
```

---

## 💻 Language Example

```clara
# Production Web Application Deployment
CLOUD AWS {
    REGION ap-south-1

    SERVER web_server {
        CPU 4
        MEMORY 16GB
        STORAGE 100GB
    }

    DATABASE main_db {
        STORAGE 500GB
    }
}
```

---

## 📁 Repository Structure

```text
CLARA/
├── include/                  # Public C headers
│   ├── ast/ast.h             # Abstract Syntax Tree definitions
│   ├── parser/parser.h       # Recursive-descent parser interface
│   ├── semantic/semantic.h   # Semantic analysis context & validation
│   ├── semantic/symbol_table.h # Hash-based symbol table
│   ├── tokens.h              # Lexer token enumerations
│   └── ir/ir.h               # Intermediate Representation schema
├── src/                      # Implementation sources
│   ├── lexer/lexer.l         # Flex lexical analyzer specification
│   ├── parser/parser.c       # Grammar parser implementation
│   ├── ast/ast.c             # AST node creation and traversal
│   ├── semantic/semantic.c   # Semantic checks & constraint rules
│   ├── semantic/symbol_table.c # Symbol table implementation
│   ├── ir/ir.c               # IR construction & serialization
│   └── main.c                # Unified compiler driver CLI
├── tests/                    # Test suites
│   ├── lexer/                # Lexer test cases (.clara fixtures)
│   ├── parser/               # Parser unit tests
│   └── semantic/             # Symbol table and semantic analysis tests
├── docs/                     # Specifications and architectural docs
│   ├── lexer.md              # Lexer documentation
│   ├── parser_semantic.md    # Parser, AST & semantic analysis docs
│   ├── grammar.md            # Formal EBNF grammar specification
│   └── architecture.md       # Pipeline and subsystem design
├── CMakeLists.txt            # CMake build configuration
└── README.md
```

---

## 🔨 Building and Testing

### Prerequisites
- GCC / Clang / MSVC (C99 or later)
- Flex (optional, for regenerating lexer)
- CMake 3.15+ (optional)

### Quick Build & Run (GCC / MSYS2 / MinGW)

```powershell
# Build and run the CLARA compiler driver
gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c src/parser/parser.c src/main.c -o clara.exe

# Compile and validate a CLARA file
./clara.exe tests/lexer/valid.clara

# Run test suites
gcc -Iinclude src/semantic/symbol_table.c tests/semantic/symbol_table_test.c -o symbol_test.exe; ./symbol_test.exe
gcc -Iinclude src/ast/ast.c src/semantic/symbol_table.c src/semantic/semantic.c tests/semantic/semantic_test.c -o semantic_test.exe; ./semantic_test.exe
```

---

## 📊 Implementation Roadmap

- [x] **Phase 0**: Repository & checkpoint verification
- [x] **Phase 1**: Language subset freeze & formal EBNF grammar
- [x] **Phase 2**: Complete compiler core (Lexer + Parser + AST + Semantic Analyzer integration)
- [x] **Phase 3**: Intermediate Representation (IR) and basic code generation
- [x] **Phase 4**: Dual-mode input normalization (Canonical JSON)
- [x] **Phase 5**: Constraint-aware alternatives & scoring engine
- [ ] **Phase 6**: Explainable configuration diff
- [ ] **Phase 7**: Web UI & Configuration Studio
