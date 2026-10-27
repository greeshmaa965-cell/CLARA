# CLARA Project Team Work Breakdown & Ownership Matrix

This document defines the formal division of the CLARA project among **three team members**, balancing technical workload, compiler pipeline phases, research novelties, repository files, full-stack components, and test suites.

---

## 👥 Executive Summary of Roles

```text
+-------------------------------------------------------------------------------------------------------+
|                                        CLARA COMPILER PLATFORM                                        |
+----------------------------------+----------------------------------+---------------------------------+
|        TEAMMATE 1                |        TEAMMATE 2                |        TEAMMATE 3               |
| Language Ingestion Lead          | Architecture & Semantics Lead    | Synthesis & Explanation Lead    |
+----------------------------------+----------------------------------+---------------------------------+
| • Compiler: Lexer & Parser       | • Compiler: Symbol Table &       | • Compiler: IR Generation &     |
|   (Phases 1 & 2)                 |   Semantic Analysis (Phase 3)    |   Terraform Codegen (Phases 4-5)|
| • Novelty 1: Dual-Mode Input     | • Novelty 2: Constraint-Aware    | • Novelty 3: Explainable        |
|   Normalization                  |   Alternative Generation         |   Configuration Diff Engine     |
| • UI: Dual-Mode Studio Inputs    | • UI: Candidate Comparison Cards | • UI: Rule Diff Table & Live    |
| • API: /api/normalize            | • API: /api/recommend, /catalog  |   Code Exporter (/api/compile)  |
+----------------------------------+----------------------------------+---------------------------------+
```

---

## 📋 Detailed Teammate Breakdown

### 👤 Teammate 1: Language Ingestion & Frontend Compiler Lead

> **Focus Area**: How CLARA ingests, lexes, parses, and normalizes infrastructure declarations from both formal code and plain English.

#### 1. Compiler Responsibilities
- **Phase 1: Lexical Analysis**:
  - Regular expressions and token definitions for clouds, regions, and resource types.
  - Flex lexer specification with line and column tracking for exact error reporting.
- **Phase 2: Syntax Analysis & AST Construction**:
  - Formal EBNF grammar design (`docs/grammar.md`).
  - Recursive-descent grammar parser and Abstract Syntax Tree node hierarchy.
  - Syntax error diagnostics and syntax tree traversal.

#### 2. Project Novelty Ownership
- **Novelty 1: Dual-Mode Input Normalization**:
  - Natural language heuristic extractor (vCPU, RAM, storage, regions, providers).
  - Form normalizer validating typed inputs against strict boundary schemas.
  - Canonical JSON normalization (`schema_version: "1.0"`).
  - CLARA DSL code synthesizer generating clean `.clara` files from canonical objects.

#### 3. Full-Stack & Integration Deliverables
- **Backend API**: `POST /api/normalize` endpoint.
- **Frontend UI**:
  - Dual-mode input switcher (Natural Language tab vs. Structured Form tab).
  - Preset suggestion prompts and live query input binding.
  - Canonical JSON live preview panel.

#### 4. Assigned Files & Directories
```text
include/tokens.h
include/ast/ast.h
include/parser/parser.h
src/lexer/lexer.l
src/parser/parser.c
src/ast/ast.c
src/normalization/natural_language.py
src/normalization/form_normalizer.py
src/normalization/normalizer.py
src/normalization/schema.py
tests/lexer/
tests/parser/
tests/normalization/
docs/lexer.md
docs/grammar.md
```

---

### 👤 Teammate 2: Semantic Analysis & Architecture Engine Lead

> **Focus Area**: How CLARA enforces semantic constraints, queries multi-cloud hardware catalogues, and generates multi-profile architectures.

#### 1. Compiler Responsibilities
- **Phase 3: Semantic Analysis & Symbol Table**:
  - Hash-based symbol table tracking declared cloud providers, regions, and resources.
  - Scope resolution and duplicate identifier collision detection.
  - Type-checking and hardware validation (e.g., minimum RAM, CPU positivity, valid regions).
  - Contextual semantic error reporting with source locations.

#### 2. Project Novelty Ownership
- **Novelty 2: Constraint-Aware Multi-Candidate Generation**:
  - Hardware pricing catalogue maintenance (`data/resource_catalog/catalog_snapshot.json`).
  - Hard constraint filtering engine (enforcing vCPU, RAM, disk, budget floors/ceilings).
  - Multi-profile architectural generator:
    - **Candidate A**: Cost-Optimized (baseline spend)
    - **Candidate B**: Balanced (+50% to +100% capacity headroom for spike tolerance)
    - **Candidate C**: Performance-Focused (high compute/memory bandwidth)
  - Infeasibility diagnostic engine pinpointing constraint conflicts.

#### 3. Full-Stack & Integration Deliverables
- **Backend API**: `POST /api/recommend` and `GET /api/catalog` endpoints.
- **Frontend UI**:
  - Architecture Candidate cards (Cost-Optimized, Balanced, Performance-Focused).
  - Infeasibility and conflict diagnostic alert boxes.
  - Monthly compute and storage price summaries.

#### 4. Assigned Files & Directories
```text
include/semantic/symbol_table.h
include/semantic/semantic.h
src/semantic/symbol_table.c
src/semantic/semantic.c
src/recommendations/engine.py
src/recommendations/constraints.py
data/resource_catalog/catalog_snapshot.json
tests/semantic/
tests/recommendations/
docs/parser_semantic.md
```

---

### 👤 Teammate 3: Intermediate Representation, Code Generation & Diff Lead

> **Focus Area**: How CLARA justifies recommendations with grounded explanation rules, emits intermediate representations, and generates deployable Terraform HCL.

#### 1. Compiler Responsibilities
- **Phase 4: Intermediate Representation (IR)**:
  - Strongly-typed C struct Intermediate Representation (`include/ir/ir.h`).
  - AST-to-IR lowering pass and IR JSON serialization.
- **Phase 5: Target Code Generation**:
  - Automated Terraform HCL code generation (`main.tf`) supporting AWS, Azure, and GCP.
  - Main compiler CLI driver (`src/main.c`) coordinating `--ast`, `--ir`, and `--terraform` flags.
  - Build automation (`scripts/build.ps1`, `scripts/build.sh`, `CMakeLists.txt`).

#### 2. Project Novelty Ownership
- **Novelty 3: Explainable Configuration Diff Engine**:
  - Field-by-field diff comparison between user requirements and chosen candidate.
  - Rule-grounded justification engine:
    - `WORKLOAD_CPU_HEADROOM`, `WORKLOAD_MEMORY_HEADROOM`, `INSTANCE_SHAPE_COUPLING`, `INSTANCE_MAPPING`, `COST_ESTIMATION`, `EXACT_MATCH`.
  - Multi-candidate comparative matrix output (Terminal tables & JSON).

#### 3. Full-Stack & Integration Deliverables
- **Backend API & CI/CD**:
  - Unified server driver (`server.py`), `POST /api/diff`, `POST /api/compile`, and `GET /api/health`.
  - CI/CD workflow (`.github/workflows/deploy.yml`) and remote tunnels.
- **Frontend UI**:
  - Explainable Diff table with color-coded tags (`ADDED`, `MODIFIED`, `UNCHANGED`).
  - Toggle switch for unchanged configuration rows.
  - Multi-tab code generator preview (CLARA DSL, IR JSON, Terraform) with copy-to-clipboard.

#### 4. Assigned Files & Directories
```text
include/ir/ir.h
include/codegen/codegen.h
src/ir/ir.c
src/codegen/codegen.c
src/main.c
src/config_diff/diff_engine.py
src/config_diff/rules.py
server.py
scripts/build.ps1
scripts/build.sh
CMakeLists.txt
.github/workflows/deploy.yml
tests/codegen/
tests/config_diff/
docs/architecture.md
docs/api_contracts.md
```

---

## ⚖️ Workload Equity Matrix

| Dimension | Teammate 1 | Teammate 2 | Teammate 3 |
|---|---|---|---|
| **Compiler Phases** | Phase 1 (Lexer) + Phase 2 (Parser & AST) | Phase 3 (Symbol Table & Semantic Analysis) | Phase 4 (IR) + Phase 5 (Codegen) + Driver |
| **C Code Footprint** | ~550 lines (`lexer.l`, `parser.c`, `ast.c`) | ~520 lines (`symbol_table.c`, `semantic.c`) | ~650 lines (`ir.c`, `codegen.c`, `main.c`) |
| **Novelty System** | Novelty 1: Dual-Mode Input Normalization | Novelty 2: Constraint-Aware Alternatives | Novelty 3: Explainable Configuration Diff |
| **Python Code** | ~400 lines (`src/normalization/`) | ~430 lines (`src/recommendations/`) | ~440 lines (`src/config_diff/`) |
| **API Endpoints** | `POST /api/normalize` | `POST /api/recommend`, `GET /api/catalog` | `POST /api/diff`, `POST /api/compile`, `GET /api/health` |
| **UI Components** | Input forms, NLP parser, prompt pills | Candidate cards, budget alerts, spec pills | Diff comparison table, rule badges, code export tabs |
| **Test Suites** | `tests/lexer/`, `tests/parser/`, `tests/normalization/` | `tests/semantic/`, `tests/recommendations/` | `tests/codegen/`, `tests/config_diff/` |
| **DevOps / CI** | Grammar specifications & parser docs | Catalogue snapshots & validation contracts | Build scripts (`build.ps1`), `server.py`, GitHub Actions CI |

---

## 🔄 Presentation & Demo Script Plan

When demonstrating the project during evaluation or final presentation:
1. **Teammate 1 presents first**:
   - Demonstrates input normalization: enters natural language prompt or fills form.
   - Shows AST and tokens generated by the lexer/parser.
2. **Teammate 2 presents second**:
   - Demonstrates semantic analysis and symbol table validation.
   - Explains the 3 candidate architectures generated, constraint filtering, and cost optimization trade-offs.
3. **Teammate 3 presents third**:
   - Explains the grounded rule justifications in the Diff table.
   - Shows real-time intermediate representation (IR) compilation and emitted Terraform HCL ready for `terraform apply`.
