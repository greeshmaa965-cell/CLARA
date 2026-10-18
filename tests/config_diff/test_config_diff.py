"""Automated test suite for CLARA Explainable Configuration Diff (Phase 6).
Tests change detection, explanation quality, rule ID attribution,
table exports, and full pipeline integration.
"""

import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.normalization.normalizer import normalize_request
from src.recommendations.engine import generate_alternatives
from src.config_diff.diff_engine import (
    compute_explainable_diff,
    diff_to_markdown,
    diff_to_text
)
from src.config_diff.rules import (
    RULE_WORKLOAD_MEMORY_HEADROOM,
    RULE_WORKLOAD_CPU_HEADROOM,
    RULE_INSTANCE_MAPPING,
    RULE_EXACT_MATCH
)


class TestExplainableConfigDiff(unittest.TestCase):

    def setUp(self):
        self.original_request = {
            "provider": "aws",
            "workload": "web_server",
            "region": "ap-south-1",
            "requirements": {
                "vcpu_min": 2,
                "memory_gb_min": 4.0,
                "storage_gb_min": 50.0
            },
            "optimization": {"priority": "cost", "monthly_budget": None},
            "constraints": {"must_satisfy_all": True}
        }

        self.candidate_balanced = {
            "candidate_id": "B",
            "profile": "balanced",
            "feasible": True,
            "instance_type": "t3.large",
            "resources": {
                "vcpu": 2,
                "memory_gb": 8.0,
                "storage_gb": 50.0
            },
            "cost": {
                "compute_monthly": 60.80,
                "storage_monthly": 4.00,
                "total_monthly": 64.80,
                "currency": "USD"
            }
        }

        self.candidate_perf = {
            "candidate_id": "C",
            "profile": "performance_focused",
            "feasible": True,
            "instance_type": "m6i.2xlarge",
            "resources": {
                "vcpu": 8,
                "memory_gb": 32.0,
                "storage_gb": 50.0
            },
            "cost": {
                "compute_monthly": 280.00,
                "storage_monthly": 4.00,
                "total_monthly": 284.00,
                "currency": "USD"
            }
        }

    def test_diff_detection_balanced_candidate(self):
        """Tests that RAM increase is accurately detected as modified, while vCPU and storage are unchanged."""
        diff = compute_explainable_diff(self.original_request, self.candidate_balanced)

        self.assertEqual(diff["recommended_candidate_id"], "B")
        self.assertEqual(diff["profile"], "balanced")

        changes = diff["changes"]
        # Find memory change
        mem_change = next(c for c in changes if c["field"] == "memory_gb")
        self.assertEqual(mem_change["change_type"], "modified")
        self.assertEqual(mem_change["old_value"], 4.0)
        self.assertEqual(mem_change["new_value"], 8.0)
        self.assertEqual(mem_change["rule_id"], RULE_WORKLOAD_MEMORY_HEADROOM)
        self.assertTrue(len(mem_change["reason"]) > 0)

        # Unchanged fields should include vCPU and storage
        unchanged_fields = [u["field"] for u in diff["unchanged"]]
        self.assertIn("vcpu", unchanged_fields)
        self.assertIn("storage_gb", unchanged_fields)

    def test_diff_detection_perf_candidate(self):
        """Tests that both vCPU and RAM increases are detected for performance-focused candidate."""
        diff = compute_explainable_diff(self.original_request, self.candidate_perf)

        changes = {c["field"]: c for c in diff["changes"]}
        self.assertIn("vcpu", changes)
        self.assertEqual(changes["vcpu"]["old_value"], 2)
        self.assertEqual(changes["vcpu"]["new_value"], 8)
        self.assertEqual(changes["vcpu"]["rule_id"], RULE_WORKLOAD_CPU_HEADROOM)

        self.assertIn("memory_gb", changes)
        self.assertEqual(changes["memory_gb"]["old_value"], 4.0)
        self.assertEqual(changes["memory_gb"]["new_value"], 32.0)

    def test_explanation_grounding_coverage(self):
        """Ensures every single change has a valid rule_id and clear reason."""
        diff = compute_explainable_diff(self.original_request, self.candidate_perf)
        for c in diff["changes"]:
            self.assertIsNotNone(c.get("rule_id"), f"Field {c['field']} missing rule_id")
            self.assertIsNotNone(c.get("reason"), f"Field {c['field']} missing reason")
            self.assertGreater(len(c["reason"]), 10)

    def test_markdown_and_text_export(self):
        """Tests rendering of Markdown table and ASCII text representation."""
        diff = compute_explainable_diff(self.original_request, self.candidate_balanced)

        md = diff_to_markdown(diff, show_unchanged=True)
        self.assertIn("| Field | Original | Recommended | Action | Explanation & Rule |", md)
        self.assertIn("Memory / RAM", md)
        self.assertIn("4.0 GB", md)
        self.assertIn("8.0 GB", md)

        text = diff_to_text(diff, show_unchanged=True)
        self.assertIn("CLARA CONFIGURATION DIFF", text)
        self.assertIn("MODIFIED", text)
        self.assertIn("UNCHANGED", text)

    def test_hide_unchanged_option(self):
        """Tests that hide_unchanged suppresses unchanged fields from diff."""
        diff = compute_explainable_diff(self.original_request, self.candidate_balanced, include_unchanged=False)
        self.assertNotIn("unchanged", diff)

        md = diff_to_markdown(diff, show_unchanged=False)
        self.assertNotIn("UNCHANGED", md)

    def test_end_to_end_full_pipeline(self):
        """Tests the complete pipeline: Natural Language -> Normalization -> Recommendations -> Explainable Diff."""
        nl_text = "I need an AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50 GB storage."

        # 1. Normalization (Phase 4)
        norm_res = normalize_request({"mode": "natural_language", "input": {"text": nl_text}})
        self.assertFalse(norm_res["needs_clarification"])
        canonical_req = norm_res["normalized_request"]

        # 2. Alternatives Generation (Phase 5)
        alt_res = generate_alternatives(canonical_req)
        self.assertEqual(alt_res["status"], "SUCCESS")

        # Pick Candidate B (Balanced)
        cand_b = next(c for c in alt_res["candidates"] if c["profile"] == "balanced")

        # 3. Explainable Diff (Phase 6)
        diff = compute_explainable_diff(canonical_req, cand_b)
        self.assertEqual(diff["recommended_candidate_id"], cand_b["candidate_id"])
        self.assertGreater(len(diff["changes"]), 0)


if __name__ == "__main__":
    unittest.main()
