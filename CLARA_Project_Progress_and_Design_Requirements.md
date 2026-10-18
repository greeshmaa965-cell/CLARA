# CLARA --- Project State, Architecture, Novelty Features & UI Design Requirements

> **Project name:** CLARA --- Cloud Language, Analysis, and Resource
> Architecture\
> **Project type:** Compiler-based Domain-Specific Language (DSL) for
> cloud configuration and recommendation\
> **Document purpose:** Continue the project from the previously
> recorded state, capture the three agreed novelty features, and define
> the frontend design requirements based on the supplied visual
> reference and HTML/CSS template.

------------------------------------------------------------------------

## 1. Project Overview

CLARA is a compiler-based Domain-Specific Language (DSL) intended to let
users describe cloud infrastructure in a beginner-friendly way. The
system parses a CLARA configuration, validates its structure and
meaning, transforms it into an intermediate representation (IR), and
produces cloud-oriented output.

The planned scope includes:

-   A lexer that converts source text into tokens.
-   A parser that checks the grammar and builds an Abstract Syntax Tree
    (AST).
-   Semantic analysis and a symbol table to validate configuration
    meaning.
-   An intermediate representation and code-generation layer.
-   Cloud-provider mapping, initially for a deliberately limited set of
    AWS, Azure, and GCP resources.
-   A recommendation layer that can compare feasible configurations.
-   A user interface that accepts both natural-language requests and
    structured form input.
-   Explanations that show why a recommendation differs from the user's
    original configuration.

**Scope rule:** Complete and test the core compiler pipeline before
attempting advanced cloud integrations or ML. Keep the first version
small enough to test end-to-end.

## 2. Previously Recorded Repository State

The last recorded repository checkpoint was:

-   Repository: `https://github.com/greeshmaa965-cell/CLARA`
-   `main` was kept as the base/project-structure branch.
-   `dev` and `feature/lexer` were recorded at commit `12c629a` ---
    `Complete CLARA lexer and token interface`.
-   `main` was recorded at commit `227489a` and did not yet contain
    `src/lexer`.
-   The lexer work was recorded as including:
    -   `src/lexer/lexer.l`
    -   `include/tokens.h`
    -   `docs/lexer.md`
    -   Lexer test inputs: `comments.clara`, `edge_cases.clara`,
        `invalid.clara`, and `valid.clara`

This is the **last known checkpoint from prior project notes**, not a
live check of the repository. Confirm the current branch and commit
before continuing. The parser, AST, semantic analyzer, IR, and
recommendation features should be treated as **planned/not verified as
implemented** unless the current repository proves otherwise.

### Suggested Git workflow

``` text
main
└── dev
    ├── feature/lexer
    ├── feature/parser-semantic
    ├── feature/ir-codegen
    ├── feature/input-normalization
    ├── feature/config-recommendations
    └── feature/config-diff
```

Create feature branches from the team's agreed integration branch, open
pull requests, test the integration branch, and merge into `main` only
when the team is ready to release.

## 3. Team Responsibilities and Integration Contract

  -----------------------------------------------------------------------
  Team area               Main responsibility     Required output
  ----------------------- ----------------------- -----------------------
  Lexer                   Recognize keywords,     Token stream with token
                          identifiers, values,    type, value, and source
                          separators, comments,   location
                          and invalid characters  

  Parser / AST / semantic Grammar, parsing, AST,  Validated AST or
  analysis                symbol table, semantic  structured diagnostics
                          rules, diagnostic       
                          reporting               

  IR / code generation /  Convert validated AST   IR, generated output,
  cloud mapping           to IR and               and mapping metadata
                          provider-oriented       
                          output                  

  Shared product features Input normalization,    Consistent
                          alternatives,           request/response
                          configuration diff, UI  contracts across
                          integration, tests      frontend and backend
  -----------------------------------------------------------------------

The team has discussed a hand-written parser as an option. The parser
language and lexer/parser boundary must be confirmed before
implementation. Flex is traditionally integrated with C, so if the
parser is written in another language, agree on a stable token interface
or JSON boundary rather than assuming direct in-process integration.

## 4. Core Compiler Architecture

``` text
User input
  ├── Natural-language request
  └── Structured service-selection form
              ↓
      Input normalization
              ↓
     Canonical request JSON
              ↓
     CLARA configuration / DSL
              ↓
       Flex-based lexer
              ↓
            Tokens
              ↓
           Parser
              ↓
             AST
              ↓
      Symbol table + semantic checks
              ↓
       Validated AST + diagnostics
              ↓
       Intermediate representation
              ↓
     Candidate configuration engine
              ↓
 Constraint validation and scoring
              ↓
 Multiple feasible alternatives
              ↓
 Explainable configuration diff
              ↓
 UI: compare, inspect, and select
              ↓
 Cloud-oriented output / export
```

The natural-language path may use an LLM or a controlled
intent-extraction component, but it must **not bypass validation**. Both
input modes must produce the same canonical JSON schema and then pass
through the same validation and recommendation pipeline.

## 5. Example CLARA Configuration

The current project notes use this example as a simple cloud
configuration:

``` text
CLOUD AWS

SERVER web1
CPU 4
MEMORY 16
STORAGE 100
REGION Mumbai
```

The precise grammar, supported values, units, and cloud-provider region
names still need to be finalized by the team. Treat this as an
illustrative example, not a claim that all values are already validated
or supported.

------------------------------------------------------------------------

# 6. Three Novelty Features to Add

These are proposed product features. They are **not marked implemented**
until code and tests demonstrate them.

## Novelty 1 --- Dual-Mode Input Normalization

**Difficulty:** Medium\
**Priority:** High\
**Goal:** Let users describe what they need in natural language or
choose options in a structured form. Convert both inputs into the same
canonical JSON representation.

### User experience

**Natural-language example**

> I need a small AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50
> GB storage. Keep the monthly cost low.

**Structured-form example**

-   Cloud provider: AWS
-   Workload: Web server
-   Region: Mumbai (or the provider's validated region identifier)
-   vCPU: 2
-   Memory: 4 GB
-   Storage: 50 GB
-   Priority: Lowest feasible cost

Both should normalize to a single schema, for example:

``` json
{
  "provider": "aws",
  "workload": "web_server",
  "region": "user_selected_region",
  "requirements": {
    "vcpu_min": 2,
    "memory_gb_min": 4,
    "storage_gb_min": 50
  },
  "optimization": {
    "priority": "cost",
    "monthly_budget": null
  },
  "constraints": {
    "must_satisfy_all": true
  }
}
```

The region string above is a placeholder. Replace it with a real,
provider-specific region identifier only after region mapping is
defined.

### Functional requirements

1.  Provide a natural-language text input.
2.  Provide a structured form for the same supported requirements.
3.  Normalize both modes to the same versioned JSON schema.
4.  Validate required fields, value types, ranges, units, and supported
    provider/workload combinations.
5.  Ask for clarification when important values are missing or
    ambiguous; do not silently invent requirements.
6.  Preserve the user's explicit constraints and optimization priority.
7.  Show the normalized request to the user before generating
    recommendations, or make it inspectable.
8.  Record the input mode for diagnostics/analytics without changing the
    canonical requirements.
9.  Return field-level validation messages when normalization fails.

### Suggested API contract

`POST /api/normalize`

Request:

``` json
{
  "mode": "form",
  "input": {
    "provider": "aws",
    "workload": "web_server",
    "region": "user_selected_region",
    "vcpu_min": 2,
    "memory_gb_min": 4,
    "storage_gb_min": 50,
    "optimization_priority": "cost"
  }
}
```

For natural language, `mode` may be `natural_language` and `input` may
contain a `text` field.

Successful response:

``` json
{
  "schema_version": "1.0",
  "normalized_request": {
    "provider": "aws",
    "workload": "web_server",
    "region": "user_selected_region",
    "requirements": {
      "vcpu_min": 2,
      "memory_gb_min": 4,
      "storage_gb_min": 50
    },
    "optimization": {
      "priority": "cost",
      "monthly_budget": null
    },
    "constraints": {
      "must_satisfy_all": true
    }
  },
  "warnings": [],
  "needs_clarification": false
}
```

### Acceptance criteria

-   Equivalent form and natural-language requests produce equivalent
    canonical requirements.
-   Invalid types, unsupported values, and ambiguous requests are
    reported clearly.
-   The recommendation engine consumes only the canonical schema, not
    separate mode-specific objects.
-   Tests cover valid input, missing fields, malformed values, ambiguous
    natural language, and conflicting constraints.

------------------------------------------------------------------------

## Novelty 2 --- Constraint-Aware Alternative Generation

**Difficulty:** Medium\
**Priority:** High\
**Goal:** Generate multiple feasible configurations and compare cost,
resource capacity, and performance trade-offs instead of returning only
one recommendation.

### Example alternatives

For a single normalized request, the system might produce:

  ---------------------------------------------------------------------------------------
  Candidate      Optimization profile  Cost           Capacity       Performance
  -------------- --------------------- -------------- -------------- --------------------
  A              Lowest feasible cost  Estimated      Meets all hard Suitable for
                                       monthly cost   limits         baseline workload

  B              Balanced              Estimated      More headroom  Balanced
                                       monthly cost                  latency/throughput

  C              Performance-focused   Estimated      Highest        Better for demanding
                                       monthly cost   headroom       workloads
  ---------------------------------------------------------------------------------------

These are illustrative labels only. Do not show invented prices or
performance measurements. Actual numbers must come from a versioned
dataset, provider pricing source, benchmark, or explicitly labelled
estimate.

### Functional requirements

1.  Generate more than one candidate when multiple candidates satisfy
    the request.
2.  Enforce hard constraints first: provider, region, minimum
    CPU/RAM/storage, budget ceiling, and other declared rules.
3.  Separate hard constraints from soft preferences such as "prefer
    lower cost."
4.  Score feasible candidates according to the user's optimization
    priority.
5.  Compare candidates using consistent units and assumptions.
6.  Explain why a candidate was excluded if useful, such as failing the
    memory minimum or exceeding budget.
7.  Label unknown or estimated values honestly.
8.  Keep candidate generation deterministic for the same request and
    dataset version where possible.
9.  Never label an infeasible configuration as recommended.
10. If no feasible candidate exists, report the conflict and identify
    which constraint(s) prevent a solution.

### Suggested candidate JSON

``` json
{
  "request_id": "example-request",
  "dataset_version": "pricing-snapshot-YYYY-MM-DD",
  "candidates": [
    {
      "candidate_id": "A",
      "profile": "cost_optimized",
      "feasible": true,
      "resources": {
        "vcpu": 2,
        "memory_gb": 4,
        "storage_gb": 50
      },
      "estimated_monthly_cost": null,
      "cost_currency": "USD",
      "capacity_summary": "Meets declared minimum requirements",
      "performance_summary": "Baseline estimate; benchmark not yet available",
      "constraint_results": []
    }
  ]
}
```

The null cost is intentional until a reliable pricing source is
connected. Do not substitute a guessed price.

### Suggested ranking logic

1.  Generate candidate configurations from the supported resource
    catalogue.
2.  Reject candidates that violate hard constraints.
3.  Calculate or retrieve cost estimates using a dated pricing dataset.
4.  Evaluate capacity and performance using documented rules or measured
    benchmarks.
5.  Rank the remaining candidates based on the selected preference.
6.  Return the top feasible alternatives with the assumptions and
    trade-offs attached.

A simple first version can use rules and weighted scoring; ML is not
required to deliver this feature. Add ML only if a reliable dataset and
evaluation plan justify it.

### Acceptance criteria

-   Every returned recommendation passes all hard constraints.
-   Candidate comparisons use consistent units and clearly state
    assumptions.
-   Cost and performance claims are traceable to a dataset, provider
    source, or benchmark.
-   Tests cover budget violations, insufficient resources,
    no-feasible-solution cases, ties, and different optimization
    priorities.

------------------------------------------------------------------------

## Novelty 3 --- Explainable Configuration Diff

**Difficulty:** Easy--Medium\
**Priority:** High\
**Goal:** Show exactly what changes between the user's original
configuration and a recommended configuration, and explain why each
change is proposed.

### Example

Original configuration:

``` json
{
  "vcpu": 2,
  "memory_gb": 4,
  "storage_gb": 50
}
```

Recommended configuration:

``` json
{
  "vcpu": 2,
  "memory_gb": 8,
  "storage_gb": 50
}
```

Example diff:

  -------------------------------------------------------------------------
  Field                       Original          Recommended Reason
  --------------- -------------------- -------------------- ---------------
  vCPU                               2                    2 No change
                                                            required

  Memory                          4 GB                 8 GB Candidate
                                                            requires 8 GB
                                                            to satisfy the
                                                            selected
                                                            workload rule

  Storage                        50 GB                50 GB No change
                                                            required
  -------------------------------------------------------------------------

The reason shown must be generated from the actual rule, constraint, or
scoring explanation that caused the change. This example is illustrative
and does not assert that 8 GB is always required.

### Functional requirements

1.  Compare the normalized original request/configuration with a
    selected candidate.
2.  Show added, removed, and changed fields.
3.  Include original value, proposed value, reason, and related
    constraint/rule where available.
4.  Distinguish user requirements from optimizer preferences.
5.  Mark unchanged fields clearly or hide them behind an optional "show
    unchanged" control.
6.  Make it possible to inspect the full recommended configuration.
7.  Export the diff as JSON and/or Markdown.
8.  Never claim a change is necessary unless a specific constraint or
    documented scoring reason supports it.

### Suggested diff JSON

``` json
{
  "original_candidate_id": "user_configuration",
  "recommended_candidate_id": "B",
  "changes": [
    {
      "field": "memory_gb",
      "change_type": "modified",
      "old_value": 4,
      "new_value": 8,
      "unit": "GB",
      "reason": "Satisfies the declared workload-capacity rule",
      "rule_id": "WORKLOAD_MEMORY_REQUIREMENT",
      "severity": "recommendation"
    }
  ],
  "summary": {
    "added_fields": 0,
    "removed_fields": 0,
    "modified_fields": 1
  }
}
```

### Acceptance criteria

-   Every changed field is reported accurately.
-   Each proposed change has a grounded explanation or is explicitly
    marked as a preference-based optimization.
-   Diff output is stable and machine-readable.
-   Tests cover added fields, removed fields, modified values, unchanged
    configurations, and missing explanations.

------------------------------------------------------------------------

# 7. Shared Data Contracts

To avoid mismatches between frontend and backend, define these contracts
before parallel implementation:

1.  **Canonical request JSON** --- output of input normalization.
2.  **Validation diagnostic** --- syntax/semantic errors and warnings.
3.  **Candidate configuration** --- resources, feasibility, cost
    estimate, capacity/performance summaries, and constraint results.
4.  **Configuration diff** --- field changes and explanations.
5.  **IR/output** --- the compiler backend's stable representation.

Recommended diagnostic shape:

``` json
{
  "severity": "error",
  "code": "RESOURCE_DUPLICATE_NAME",
  "line": 3,
  "column": 1,
  "resource": "web1",
  "field": "name",
  "message": "Resource name 'web1' is already declared.",
  "explanation": "Each resource name must be unique in this configuration.",
  "suggestion": "Choose a different resource name.",
  "rule_id": "UNIQUE_RESOURCE_NAME"
}
```

The line/column values should be provided by the lexer/parser where
source locations are available. For errors produced from form input,
source positions may be absent; return a field path instead.

------------------------------------------------------------------------

# 8. Frontend Design Requirements Based on the Supplied Reference

## 8.1 Visual direction

Use the supplied screenshot and HTML/CSS template as the visual
reference for the **CLARA landing/hero page**:

-   Warm dark-brown to amber/orange gradient.
-   White typography with a clean sans-serif font such as Poppins.
-   Glassmorphism: translucent cards, thin light borders, backdrop blur,
    soft shadows.
-   Large central headline and a short supporting sentence.
-   Soft steam/cloud visual behind the main card, inspired by the
    reference.
-   Minimal top navigation with the CLARA logo/name and links.
-   Small translucent pill/label, supporting text, and secondary feature
    links.
-   Responsive layout for desktop, tablet, and mobile.
-   Reduced-motion support for users who prefer less animation.

Do not copy the placeholder brand text from the template. Use **CLARA**
branding and product-appropriate copy. The steam-cloud image is a visual
motif only; the product is a cloud-configuration DSL, not a steam
product.

## 8.2 Suggested landing-page copy

**Brand:** CLARA

**Small label:** Cloud configuration, made clearer

**Hero headline:**\
`DESCRIBE. OPTIMIZE. DEPLOY.`

**Supporting text:**\
`Turn cloud requirements into validated configurations, compare feasible alternatives, and understand every recommended change.`

**Primary action:** `Start configuring`

**Secondary action:** `Explore features`

**Small supporting note:**\
`One request. Clear options. Explainable decisions.`

## 8.3 Navigation

Suggested links:

-   Home
-   How It Works
-   Features
-   Configuration Studio
-   About

Keep navigation minimal. On narrow screens, use an accessible menu
button with a visible focus state and a working open/close interaction.

## 8.4 Main product experience

The landing page should lead into a configuration workspace with these
main areas:

1.  **Input mode selector**
    -   Natural language
    -   Structured form
2.  **Requirements input**
    -   Text area for a natural-language request, or
    -   Form fields for provider, workload/resource type, region, CPU,
        memory, storage, budget, and optimization priority.
3.  **Normalized request preview**
    -   Show the canonical interpretation.
    -   Let users review requirements before recommendation generation.
4.  **Feasible alternatives**
    -   Display multiple candidates as comparable cards or rows.
    -   Compare estimated cost, capacity, performance, feasibility, and
        assumptions.
5.  **Configuration diff**
    -   Highlight added, removed, and changed values.
    -   Include a concise reason for every recommended change.
6.  **Validation and diagnostics**
    -   Show actionable errors and warnings.
    -   Include the field/resource involved and a suggested correction
        where possible.
7.  **Output/export**
    -   Show generated configuration or compiler output.
    -   Provide JSON/Markdown export where implemented.

The hero page is the entry point; the input, alternatives, and diff
views are functional product screens and should be designed as a
coherent system rather than crammed into the hero card.

## 8.5 Design tokens from the provided template

Starting values taken from the supplied HTML/CSS reference:

``` css
:root {
  --bg-1: #3b1a08;
  --bg-2: #8a4a12;
  --bg-3: #d98a2b;
  --text: #ffffff;
  --text-soft: rgba(255, 255, 255, 0.8);
  --glass: rgba(255, 255, 255, 0.08);
  --glass-border: rgba(255, 255, 255, 0.25);
  --radius: 24px;
  --font: 'Poppins', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
```

These are starting tokens, not mandatory final colors. Check text
contrast and readability, especially over the animated cloud/smoke
layer.

## 8.6 Animation and accessibility

-   Keep smoke/cloud animation behind content and set
    `pointer-events: none`.
-   Do not let the visual obscure form fields, labels, or buttons.
-   Respect `prefers-reduced-motion: reduce`.
-   Provide keyboard navigation and visible focus states.
-   Use semantic headings, navigation, buttons, labels, and form
    controls.
-   Do not use placeholder text as the only form label.
-   Ensure mobile layouts do not rely on absolute positioning for
    important content.
-   Provide loading, empty, success, and error states for API-driven
    screens.

## 8.7 UI component checklist

-   [ ] CLARA logo and responsive navigation
-   [ ] Hero headline, supporting copy, and primary CTA
-   [ ] Subtle animated cloud/smoke layer
-   [ ] Natural-language input component
-   [ ] Structured configuration form
-   [ ] Input-mode switch
-   [ ] Canonical JSON preview
-   [ ] Validation diagnostics panel
-   [ ] Candidate comparison component
-   [ ] Explainable diff component
-   [ ] Generated output preview/export
-   [ ] Responsive/mobile layout
-   [ ] Reduced-motion and keyboard accessibility

------------------------------------------------------------------------

# 9. Suggested Repository Structure

The following extends the previously proposed compiler structure to
include the three novelty features. Adapt it to the actual repository
instead of duplicating existing files.

``` text
CLARA/
├── include/
│   └── tokens.h
├── src/
│   ├── lexer/
│   │   └── lexer.l
│   ├── parser/
│   ├── ast/
│   ├── semantic/
│   ├── ir/
│   ├── codegen/
│   ├── normalization/
│   ├── recommendations/
│   ├── config_diff/
│   └── api/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── styles/
│   └── README.md
├── data/
│   ├── resource_catalog/
│   └── pricing_snapshots/
├── tests/
│   ├── lexer/
│   ├── parser/
│   ├── semantic/
│   ├── normalization/
│   ├── recommendations/
│   └── config_diff/
├── docs/
│   ├── lexer.md
│   ├── grammar.md
│   ├── architecture.md
│   ├── api_contracts.md
│   └── novelty_features.md
├── scripts/
├── .gitignore
└── README.md
```

Do not create empty folders solely to match this diagram. Add a folder
when its module is being implemented.

------------------------------------------------------------------------

# 10. Implementation Roadmap

## Phase 0 --- Verify the repository checkpoint

-   [ ] Fetch the latest repository state.
-   [ ] Check current branch and recent commits.
-   [ ] Confirm whether the lexer files and tests are present.
-   [ ] Run the existing lexer tests and record the actual results.
-   [ ] Confirm the agreed language and token interface between lexer
    and parser.

## Phase 1 --- Freeze the first CLARA language subset

-   [ ] Document supported providers and resource types.
-   [ ] Finalize grammar and valid field/value formats.
-   [ ] Define canonical resource/property names and units.
-   [ ] Agree on line/column and error-reporting conventions.
-   [ ] Add valid, syntax-invalid, and semantic-invalid examples.

## Phase 2 --- Complete compiler core

-   [ ] Implement parser.
-   [ ] Build AST nodes.
-   [ ] Implement symbol table.
-   [ ] Implement semantic validation and diagnostics.
-   [ ] Test lexer-to-parser integration.
-   [ ] Pass a validated AST to the IR module.

## Phase 3 --- IR and basic output

-   [ ] Define a stable IR schema.
-   [ ] Convert validated AST to IR.
-   [ ] Generate a basic cloud-oriented output.
-   [ ] Block output generation on fatal errors.
-   [ ] Add end-to-end tests.

## Phase 4 --- Dual-mode normalization

-   [ ] Define and version canonical request JSON.
-   [ ] Build the structured form.
-   [ ] Build natural-language extraction.
-   [ ] Add validation and clarification behavior.
-   [ ] Test equivalent requests across both modes.

## Phase 5 --- Constraint-aware alternatives

-   [ ] Build a small, documented resource catalogue.
-   [ ] Define hard constraints and soft preferences.
-   [ ] Add feasibility filtering.
-   [ ] Add cost estimation with dated data or clearly labelled
    estimates.
-   [ ] Rank multiple candidates.
-   [ ] Test no-solution and conflicting-constraint cases.

## Phase 6 --- Explainable configuration diff

-   [ ] Compare original requirements/configuration with a selected
    candidate.
-   [ ] Detect added, removed, and changed fields.
-   [ ] Attach explanations and rule identifiers.
-   [ ] Build the diff UI.
-   [ ] Test exactness and explanation coverage.

## Phase 7 --- UI integration and final evaluation

-   [ ] Implement the landing page based on the visual reference.
-   [ ] Connect frontend components to API contracts.
-   [ ] Add loading, error, and empty states.
-   [ ] Test the complete path from user input to recommendation and
    diff.
-   [ ] Document limitations and evaluation results.
-   [ ] Prepare screenshots, architecture diagram, demo script, and
    README.

------------------------------------------------------------------------

# 11. Testing and Evaluation Plan

Do not report performance figures until they have been measured.

  -----------------------------------------------------------------------
  Feature                 Test focus              Example metrics
  ----------------------- ----------------------- -----------------------
  Lexer/parser/semantic   Valid programs and      Detection rate, correct
  analysis                injected                error category, correct
                          syntax/semantic faults  source location

  Dual-mode normalization Equivalent requests     Field-level agreement,
                          submitted in form and   validation accuracy,
                          natural language        clarification rate

  Alternative generation  Candidate feasibility   Hard-constraint
                          and ranking under       satisfaction rate,
                          constraints             number of feasible
                                                  candidates, ranking
                                                  consistency

  Configuration diff      Exact change detection  Change
                          and reason quality      precision/recall,
                                                  explanation coverage,
                                                  unsupported-reason rate

  End-to-end workflow     Request through output  Success rate, latency,
                          and UI                  clear error recovery
  -----------------------------------------------------------------------

For recommendation testing, create a labelled synthetic workload corpus
and record assumptions. A reasonable starting point is a small,
manageable set of scenarios; expand it after the pipeline works. Do not
claim cloud-price accuracy without a traceable pricing source and
timestamp.

## Risks and safeguards

-   **Scope risk:** Limit initial support to a small set of resources
    and properties.
-   **Pricing risk:** Prices vary by region, usage, discounts, and time.
    Version pricing data and show assumptions.
-   **Natural-language risk:** Ambiguous requests must trigger
    clarification rather than fabricated requirements.
-   **Recommendation risk:** Enforce hard constraints before ranking.
-   **Explainability risk:** Every reason must reference a rule,
    constraint, data point, or documented scoring factor.
-   **Integration risk:** Agree on JSON schemas and error contracts
    before frontend/backend work proceeds in parallel.
-   **Novelty claims:** These capabilities are useful differentiators
    for the project, but related ideas exist in infrastructure-as-code
    tooling. Demonstrate the specific implementation and measured
    benefits rather than claiming the concepts themselves are
    unprecedented.

------------------------------------------------------------------------

# 12. Definition of Done

CLARA's first meaningful end-to-end milestone is complete when:

-   [ ] A supported CLARA input is tokenized.
-   [ ] The parser builds an AST.
-   [ ] Semantic analysis returns clear errors/warnings or a validated
    AST.
-   [ ] The IR/backend consumes the validated representation.
-   [ ] Both natural-language and structured-form requests normalize to
    the same canonical JSON schema.
-   [ ] The system generates multiple candidates only when they satisfy
    hard constraints.
-   [ ] Candidates can be compared using sourced or explicitly estimated
    metrics.
-   [ ] The configuration diff identifies exact changes and gives
    grounded reasons.
-   [ ] The frontend displays the input, validation, alternatives, and
    diff coherently.
-   [ ] Automated tests cover success, invalid input, conflicting
    constraints, and no feasible candidate.
-   [ ] README and demo instructions describe what is implemented versus
    planned.

## Current status summary

**Last previously recorded implemented checkpoint:** lexer/token
interface and lexer tests on `dev` / `feature/lexer` at commit
`12c629a`.

**Needs live verification:** current branch/commit, current test
results, and whether any parser/backend work has been added since that
checkpoint.

**Planned next steps:** verify the repository, freeze the language/token
contract, complete parser + AST + semantic validation, and then
implement the three novelty features against shared JSON contracts.

**Do not describe a planned feature as completed on the resume or in the
final project report until it has been implemented and tested.**
