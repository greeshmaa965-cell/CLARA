# CLARA Shared Data Contracts & API Specification

This document defines the versioned JSON contracts connecting frontend components, normalization endpoints, recommendation engines, and compiler backends.

---

## 1. Canonical Request JSON (`POST /api/normalize`)

Produced by Input Normalization (`src/normalization/`) from natural language or form inputs:

```json
{
  "schema_version": "1.0",
  "input_mode": "natural_language",
  "normalized_request": {
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
  },
  "clara_dsl": "CLOUD AWS {\n    REGION ap-south-1\n    SERVER web_server {\n        CPU 2\n        MEMORY 4GB\n        STORAGE 50GB\n    }\n}",
  "warnings": [],
  "errors": [],
  "needs_clarification": false,
  "clarification_prompt": null
}
```

---

## 2. Candidate Configuration JSON (`POST /api/recommend`)

Produced by Candidate Generator (`src/recommendations/`):

```json
{
  "request_id": "clara-req-001",
  "dataset_version": "pricing-snapshot-2026-10-18",
  "status": "SUCCESS",
  "optimization_priority": "cost",
  "provider": "aws",
  "region": "ap-south-1",
  "total_feasible_count": 8,
  "recommended_candidate_id": "A",
  "candidates": [
    {
      "candidate_id": "A",
      "profile": "cost_optimized",
      "feasible": true,
      "instance_type": "t3.medium",
      "family": "burstable",
      "resources": {
        "vcpu": 2,
        "memory_gb": 4.0,
        "storage_gb": 50.0
      },
      "cost": {
        "compute_monthly": 30.40,
        "storage_monthly": 4.00,
        "total_monthly": 34.40,
        "currency": "USD"
      },
      "capacity_summary": "Meets declared minimum requirements with lowest resource cost.",
      "performance_summary": "Baseline compute; ideal for developmental or cost-sensitive workloads.",
      "tradeoff_notes": "Lowest price point, but lower headroom for bursty load spikes.",
      "constraint_results": [
        {"constraint": "vCPU >= 2", "actual": "2 vCPU", "passed": true},
        {"constraint": "Memory >= 4.0 GB", "actual": "4.0 GB", "passed": true},
        {"constraint": "Storage >= 50.0 GB", "actual": "50.0 GB", "passed": true}
      ]
    }
  ]
}
```

---

## 3. Configuration Diff JSON (`POST /api/diff`)

Produced by Configuration Diff Engine (`src/config_diff/`):

```json
{
  "original_candidate_id": "user_configuration",
  "recommended_candidate_id": "B",
  "profile": "balanced",
  "summary": {
    "total_changes": 3,
    "modified_fields": 1,
    "added_fields": 2,
    "unchanged_fields": 2
  },
  "changes": [
    {
      "field": "memory_gb",
      "display_name": "Memory / RAM",
      "change_type": "modified",
      "old_value": 4.0,
      "new_value": 8.0,
      "unit": "GB",
      "reason": "Allocated 8.0 GB RAM (up from 4.0 GB) to provide a comfortable operational buffer.",
      "rule_id": "WORKLOAD_MEMORY_HEADROOM",
      "severity": "recommendation"
    },
    {
      "field": "instance_type",
      "display_name": "Instance Hardware Type",
      "change_type": "added",
      "old_value": null,
      "new_value": "t3.large",
      "unit": null,
      "reason": "Selected provider hardware offering 't3.large' to fulfill required resources.",
      "rule_id": "INSTANCE_MAPPING",
      "severity": "info"
    }
  ],
  "unchanged": [
    {
      "field": "vcpu",
      "display_name": "vCPU Cores",
      "value": 2,
      "unit": "cores",
      "reason": "No change required: exact match with declared requirements.",
      "rule_id": "EXACT_MATCH"
    }
  ]
}
```

---

## 4. Compiler Intermediate Representation JSON (`clara --ir <file.clara>`)

Produced by the CLARA C compiler backend (`src/ir/`):

```json
{
  "schema_version": "1.0",
  "provider": "aws",
  "region": "ap-south-1",
  "resources": {
    "servers": [
      {
        "name": "web_server",
        "cpu": 4,
        "memory_gb": 16.00,
        "storage_gb": 100.00
      }
    ],
    "databases": [
      {
        "name": "main_db",
        "cpu": 0,
        "memory_gb": 0.00,
        "storage_gb": 500.00
      }
    ]
  }
}
```
