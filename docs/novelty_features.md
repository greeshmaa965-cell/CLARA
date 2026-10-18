# CLARA Novelty Features Specification & Guide

This document provides a comprehensive reference for the three novelty capabilities implemented in the CLARA compiler platform.

---

## Novelty 1: Dual-Mode Input Normalization (Phase 4)

### Purpose
Allows users to express cloud infrastructure requirements either through natural language or through structured web forms. Both inputs are normalized into an identical, versioned canonical JSON schema, ensuring that the recommendation and compiler engines process a single source of truth without bypassing validation.

### Architecture
- **Natural Language Extractor** (`src/normalization/natural_language.py`):
  Extracts provider, workload, region, CPU, memory, storage, optimization priorities, and budget ceilings.
- **Form Normalizer** (`src/normalization/form_normalizer.py`):
  Validates structured form inputs against typed constraints.
- **CLARA DSL Synthesizer** (`src/normalization/normalizer.py`):
  Generates verified `.clara` DSL code from canonical JSON.

### Canonical Schema (`schema_version = "1.0"`)
```json
{
  "schema_version": "1.0",
  "provider": "aws",
  "workload": "web_server",
  "region": "ap-south-1",
  "requirements": {
    "vcpu_min": 2,
    "memory_gb_min": 4.0,
    "storage_gb_min": 50.0
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

---

## Novelty 2: Constraint-Aware Alternative Generation (Phase 5)

### Purpose
Rather than returning a single opaque recommendation, CLARA generates multiple feasible architectural candidates across cost, capacity, and performance profiles.

### Architectural Candidates
1. **Candidate A (`cost_optimized`)**:
   Smallest viable instance satisfying all hard minimums with lowest monthly expenditure.
2. **Candidate B (`balanced`)**:
   Provides +50% to +100% capacity headroom for unexpected traffic spikes and production stability.
3. **Candidate C (`performance_focused`)**:
   High compute capacity and memory bandwidth for throughput-intensive services.

### Hard Constraint Enforcement & Conflict Diagnosis
- Candidates violating declared CPU, RAM, storage, or monthly budget ceilings are strictly rejected.
- When no candidate is feasible (e.g. demanding 8 vCPUs and 32 GB RAM under a $15/mo budget), the engine provides an actionable conflict diagnostic identifying the exact constraint conflict and suggesting minimum viable budgets.

---

## Novelty 3: Explainable Configuration Diff (Phase 6)

### Purpose
Provides transparent, rule-grounded justifications for every single change between the user's initial configuration and the recommended architecture.

### Grounded Rule Identifiers
| Rule ID | Category | Explanation Grounding |
|---|---|---|
| `WORKLOAD_MEMORY_HEADROOM` | Memory | Scaled RAM to provide operational buffer and avoid OOM faults. |
| `WORKLOAD_CPU_HEADROOM` | Compute | Scaled vCPU to absorb concurrent traffic spikes. |
| `INSTANCE_SHAPE_COUPLING` | Hardware | Adjustment mandated by fixed provider hardware ratios. |
| `STORAGE_ALIGNMENT` | Storage | Adjusted disk volume to align with provider minimums. |
| `INSTANCE_MAPPING` | Offering | Selected cloud provider instance type satisfying requirements. |
| `COST_ESTIMATION` | Pricing | Transparent itemized pricing from dated catalogue snapshot. |
| `EXACT_MATCH` | Unchanged | Exact match with user declaration; no modification required. |

### CLI Usage Example
```powershell
# Side-by-side comparative matrix across all 3 candidates
python -m src.config_diff.diff_engine --text "I need an AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50 GB storage." --matrix

# Itemized explainable diff for Candidate B (Balanced)
python -m src.config_diff.diff_engine --text "I need an AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50 GB storage." --candidate B
```
