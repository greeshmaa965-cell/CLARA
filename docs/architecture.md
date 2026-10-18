# CLARA Compiler Architecture

CLARA (**C**loud **L**anguage, **A**nalysis, and **R**esource **A**rchitecture) is a domain-specific compiler and recommendation system designed to make cloud infrastructure declarative, validated, and explainable.

---

## 1. Compiler Pipeline

```text
User Input:
  ├── Natural Language Query
  └── Structured Selection Form
              ↓
  Input Normalization (Canonical JSON)
              ↓
   CLARA DSL Source File (.clara)
              ↓
    Lexical Analyzer (Flex / yylex)
              ↓
         Token Stream
              ↓
      Parser (Syntactic Check)
              ↓
   Abstract Syntax Tree (ASTNode)
              ↓
Semantic Analysis & Symbol Table Validation
              ↓
       Validated AST
              ↓
 Intermediate Representation (IR Engine)
              ↓
 Candidate Generator & Recommendation Engine
              ↓
 Explainable Configuration Diff & Cost Matrix
              ↓
 Target Output (Terraform / Provider JSON / K8s)
```

---

## 2. Core Compiler Modules

| Subsystem | Source Location | Headers | Description |
|---|---|---|---|
| **Lexer** | `src/lexer/lexer.l` | `include/tokens.h` | Tokenizes source streams into reserved keywords, identifiers, numbers, units, and symbols. |
| **Parser** | `src/parser/parser.c` | `include/parser/parser.h` | Enforces grammar, handles syntax diagnostics, and builds the hierarchical `ASTNode` tree. |
| **AST** | `src/ast/ast.c` | `include/ast/ast.h` | Represents program structure in memory with nodes for Cloud, Server, Database, Region, CPU, Memory, and Storage. |
| **Symbol Table** | `src/semantic/symbol_table.c` | `include/semantic/symbol_table.h` | Fast hash-table lookup for cloud, server, and database identifiers to prevent conflicts and ensure unique scopes. |
| **Semantic Analyzer** | `src/semantic/semantic.c` | `include/semantic/semantic.h` | Validates resource hierarchies, bounds (>0), mandatory units, and scoping. |
| **Intermediate Representation (IR)** | `src/ir/ir.c` | `include/ir/ir.h` | Translates validated AST into target-independent canonical data structures. |
| **Code Generation** | `src/codegen/codegen.c` | `include/codegen/codegen.h` | Produces cloud provider artifacts (Terraform HCL, CloudFormation, Kubernetes specs). |

---

## 3. The Three Novelty Features

1. **Dual-Mode Input Normalization**:
   - Converts natural-language descriptions or structured form selections into a unified canonical JSON schema.
   - Prevents bypass of validation rules.
2. **Constraint-Aware Alternative Generation**:
   - Compares multiple feasible cloud resource configurations across cost, capacity, and performance.
   - Eliminates configurations that violate hard constraints.
3. **Explainable Configuration Diff**:
   - Explicitly compares user configurations against optimized recommendations with field-level justifications.
