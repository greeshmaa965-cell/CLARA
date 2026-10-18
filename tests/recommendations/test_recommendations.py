"""Automated test suite for CLARA Constraint-Aware Alternative Generation (Phase 5).
Tests multi-candidate generation, hard constraint enforcement, budget ceilings,
conflict diagnosis, and priority ranking.
"""

import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.normalization.normalizer import normalize_request
from src.recommendations.engine import generate_alternatives


class TestConstraintAwareAlternatives(unittest.TestCase):

    def setUp(self):
        self.canonical_aws = {
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
                "monthly_budget": None
            },
            "constraints": {
                "must_satisfy_all": True
            }
        }

    def test_multi_candidate_generation_aws(self):
        """Verifies that 3 distinct candidates are produced across cost, balanced, and performance profiles."""
        result = generate_alternatives(self.canonical_aws)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(len(result["candidates"]), 3)

        profiles = [c["profile"] for c in result["candidates"]]
        self.assertIn("cost_optimized", profiles)
        self.assertIn("balanced", profiles)
        self.assertIn("performance_focused", profiles)

        # Candidate A must meet all minimum hard requirements
        cand_a = next(c for c in result["candidates"] if c["profile"] == "cost_optimized")
        self.assertGreaterEqual(cand_a["resources"]["vcpu"], 2)
        self.assertGreaterEqual(cand_a["resources"]["memory_gb"], 4.0)
        self.assertGreaterEqual(cand_a["resources"]["storage_gb"], 50.0)
        self.assertGreater(cand_a["cost"]["total_monthly"], 0)

    def test_multi_candidate_generation_azure_and_gcp(self):
        """Verifies multi-candidate generation works across other supported clouds."""
        azure_req = dict(self.canonical_aws)
        azure_req["provider"] = "azure"
        azure_res = generate_alternatives(azure_req)
        self.assertEqual(azure_res["status"], "SUCCESS")
        self.assertEqual(len(azure_res["candidates"]), 3)

        gcp_req = dict(self.canonical_aws)
        gcp_req["provider"] = "gcp"
        gcp_res = generate_alternatives(gcp_req)
        self.assertEqual(gcp_res["status"], "SUCCESS")
        self.assertEqual(len(gcp_res["candidates"]), 3)

    def test_hard_constraint_enforcement(self):
        """Verifies that every candidate passes hard constraints."""
        result = generate_alternatives(self.canonical_aws)
        for cand in result["candidates"]:
            self.assertTrue(cand["feasible"])
            self.assertGreaterEqual(cand["resources"]["vcpu"], 2)
            self.assertGreaterEqual(cand["resources"]["memory_gb"], 4.0)
            self.assertGreaterEqual(cand["resources"]["storage_gb"], 50.0)

            # Check constraint audit trail
            for check in cand["constraint_results"]:
                self.assertTrue(check["passed"], f"Constraint {check['constraint']} failed unexpectedly")

    def test_budget_ceiling_enforcement(self):
        """Verifies that candidates exceeding budget are excluded."""
        budget_req = dict(self.canonical_aws)
        # t3.medium with 50GB storage costs 30.40 + 4.00 = 34.40. Budget of 40 limits options to smaller instances.
        budget_req["optimization"] = {"priority": "cost", "monthly_budget": 40.0}

        result = generate_alternatives(budget_req)
        self.assertEqual(result["status"], "SUCCESS")
        for cand in result["candidates"]:
            self.assertLessEqual(cand["cost"]["total_monthly"], 40.0)

    def test_infeasible_conflict_diagnosis(self):
        """Verifies diagnosis when declared requirements and budget conflict."""
        infeasible_req = dict(self.canonical_aws)
        # 8 vCPU + 32GB RAM cannot be met under $15/month
        infeasible_req["requirements"] = {"vcpu_min": 8, "memory_gb_min": 32.0, "storage_gb_min": 100.0}
        infeasible_req["optimization"] = {"priority": "cost", "monthly_budget": 15.0}

        result = generate_alternatives(infeasible_req)
        self.assertEqual(result["status"], "INFEASIBLE")
        self.assertEqual(len(result["candidates"]), 0)
        self.assertIn("conflict_diagnosis", result)
        self.assertEqual(result["conflict_diagnosis"]["conflict_type"], "BUDGET_EXCEEDED")
        self.assertIn("insufficient", result["message"].lower())

    def test_ranking_by_priority(self):
        """Verifies that priority ranking accurately reorders candidates."""
        # Cost priority: cheapest first
        cost_req = dict(self.canonical_aws)
        cost_req["optimization"] = {"priority": "cost", "monthly_budget": None}
        cost_res = generate_alternatives(cost_req)
        self.assertEqual(cost_res["candidates"][0]["profile"], "cost_optimized")

        # Performance priority: highest capacity first
        perf_req = dict(self.canonical_aws)
        perf_req["optimization"] = {"priority": "performance", "monthly_budget": None}
        perf_res = generate_alternatives(perf_req)
        self.assertEqual(perf_res["candidates"][0]["profile"], "performance_focused")

    def test_pipeline_chaining_from_natural_language(self):
        """Verifies chaining from Phase 4 Natural Language input directly into Phase 5 Alternatives."""
        nl_input = "I need an AWS web server in Mumbai with 4 vCPUs, 16 GB RAM, and 100 GB storage. Prioritize performance."
        norm_result = normalize_request({"mode": "natural_language", "input": {"text": nl_input}})
        self.assertFalse(norm_result["needs_clarification"])
        canonical_req = norm_result["normalized_request"]

        alt_result = generate_alternatives(canonical_req)
        self.assertEqual(alt_result["status"], "SUCCESS")
        self.assertEqual(alt_result["optimization_priority"], "performance")
        self.assertEqual(len(alt_result["candidates"]), 3)
        self.assertGreaterEqual(alt_result["candidates"][0]["resources"]["vcpu"], 4)
        self.assertGreaterEqual(alt_result["candidates"][0]["resources"]["memory_gb"], 16.0)


if __name__ == "__main__":
    unittest.main()
