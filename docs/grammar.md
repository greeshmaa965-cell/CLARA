# CLARA DSL Grammar Specification

This document defines the formal grammar for the CLARA Domain-Specific Language (DSL).

---

## 1. Lexical Grammar

### Keywords (Case-Sensitive)
```text
CLOUD      ::= "CLOUD"
SERVER     ::= "SERVER"
DATABASE   ::= "DATABASE"
REGION     ::= "REGION"
CPU        ::= "CPU"
MEMORY     ::= "MEMORY"
STORAGE    ::= "STORAGE"
```

### Identifiers & Literals
```text
LETTER            ::= [a-zA-Z_]
DIGIT             ::= [0-9]
IDENTIFIER        ::= LETTER (LETTER | DIGIT | "-" | "_")*
NUMBER            ::= DIGIT+
UNIT              ::= "MB" | "GB" | "TB"
```

### Delimiters & Ignored Tokens
```text
LBRACE            ::= "{"
RBRACE            ::= "}"
COMMENT           ::= "#" [^\r\n]*
WHITESPACE        ::= [ \t\r\n]+
```

---

## 2. Syntactic Grammar (EBNF)

A CLARA program consists of one or more cloud block specifications:

```ebnf
Program           ::= CloudBlock*

CloudBlock        ::= "CLOUD" Identifier "{" CloudItem* "}"

CloudItem         ::= RegionDecl
                    | ServerBlock
                    | DatabaseBlock

RegionDecl        ::= "REGION" Identifier

ServerBlock       ::= "SERVER" Identifier "{" ServerItem* "}"

ServerItem        ::= CpuDecl
                    | MemoryDecl
                    | StorageDecl

DatabaseBlock     ::= "DATABASE" Identifier "{" DatabaseItem* "}"

DatabaseItem      ::= StorageDecl
                    | CpuDecl
                    | MemoryDecl

CpuDecl           ::= "CPU" NUMBER

MemoryDecl        ::= "MEMORY" NUMBER UNIT?

StorageDecl       ::= "STORAGE" NUMBER UNIT?
```

---

## 3. Example Valid Programs

### Simple Multi-Tier Web Architecture
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

### Multi-Region Multi-Resource Specification
```clara
CLOUD Azure {
    REGION centralindia

    SERVER app_server {
        CPU 8
        MEMORY 32GB
        STORAGE 250GB
    }

    DATABASE cache_db {
        CPU 2
        MEMORY 8GB
        STORAGE 50GB
    }
}
```

---

## 4. Error Categories

1. **Lexical Errors**: Characters not matching keywords, identifiers, numbers, units, or valid delimiters.
2. **Syntactic Errors**: Misplaced tokens, unclosed braces, or missing identifiers.
3. **Semantic Errors**:
   - Duplicate resource names in the symbol table.
   - Declaring servers or databases outside a `CLOUD` block.
   - Specifying non-positive values (`<= 0`) for CPU, Memory, or Storage.
   - Missing measurement units on Memory or Storage allocations.
