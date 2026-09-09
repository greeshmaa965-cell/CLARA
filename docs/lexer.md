# CLARA Lexer

## 1. Purpose

The CLARA lexer performs lexical analysis on CLARA source code.

It reads the source program and converts the input characters into meaningful tokens.

These tokens are later consumed by the parser.

---

## 2. Token Categories

| CLARA Input | Token |
|---|---|
| CLOUD | TOKEN_CLOUD |
| SERVER | TOKEN_SERVER |
| DATABASE | TOKEN_DATABASE |
| CPU | TOKEN_CPU |
| MEMORY | TOKEN_MEMORY |
| STORAGE | TOKEN_STORAGE |
| REGION | TOKEN_REGION |
| Identifier | TOKEN_IDENTIFIER |
| Integer | TOKEN_NUMBER |
| MB / GB / TB | TOKEN_UNIT |
| `{` | TOKEN_LBRACE |
| `}` | TOKEN_RBRACE |

---

## 3. Keywords

The following reserved words are recognized by the lexer:

- CLOUD
- SERVER
- DATABASE
- CPU
- MEMORY
- STORAGE
- REGION

For example:

```text
SERVER
