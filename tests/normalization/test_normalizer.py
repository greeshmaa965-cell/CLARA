"""Automated test suite for CLARA Dual-Mode Normalization (Phase 4).
Tests form normalization, natural-language extraction, cross-mode equivalence,
clarification triggers, and compiler integration.
"""

import os
import sys
import json
import subprocess
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.normalization.normalizer import normalize_request, canonical_to_clara_dsl


class TestDualModeNormalization(unittest.TestCase):

    def test_form_normalization_valid(self):
        payload = {
            "mode": "form",
            "input": {
                "provider": "aws",
                "workload": "web_server",
                "region": "Mumbai",
                "vcpu_min": 2,
                "memory_gb_min": 4,
                "storage_gb_min": 50,
                "optimization_priority": "cost"
            }
        }
        res = normalize_request(payload)
        self.assertEqual(res["schema_version"], "1.0")
        self.assertFalse(res["needs_clarification"])
        self.assertEqual(len(res["errors"]), 0)

        req = res["normalized_request"]
        self.assertEqual(req["provider"], "aws")
        self.assertEqual(req["workload"], "web_server")
        self.assertEqual(req["region"], "ap-south-1")
        self.assertEqual(req["requirements"]["vcpu_min"], 2)
        self.assertEqual(req["requirements"]["memory_gb_min"], 4.0)
        self.assertEqual(req["requirements"]["storage_gb_min"], 50.0)
        self.assertEqual(req["optimization"]["priority"], "cost")

    def test_natural_language_extraction_valid(self):
        nl_text = "I need a small AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50 GB storage. Keep the monthly cost low."
        payload = {
            "mode": "natural_language",
            "input": {"text": nl_text}
        }
        res = normalize_request(payload)
        self.assertEqual(res["schema_version"], "1.0")
        self.assertFalse(res["needs_clarification"])
        self.assertEqual(len(res["errors"]), 0)

        req = res["normalized_request"]
        self.assertEqual(req["provider"], "aws")
        self.assertEqual(req["workload"], "web_server")
        self.assertEqual(req["region"], "ap-south-1")
        self.assertEqual(req["requirements"]["vcpu_min"], 2)
        self.assertEqual(req["requirements"]["memory_gb_min"], 4.0)
        self.assertEqual(req["requirements"]["storage_gb_min"], 50.0)
        self.assertEqual(req["optimization"]["priority"], "cost")

    def test_cross_mode_equivalence(self):
        """Verifies that equivalent form and natural language requests yield identical canonical requirements."""
        form_payload = {
            "mode": "form",
            "input": {
                "provider": "aws",
                "workload": "web_server",
                "region": "mumbai",
                "vcpu_min": 2,
                "memory_gb_min": 4,
                "storage_gb_min": 50,
                "optimization_priority": "cost"
            }
        }
        nl_payload = {
            "mode": "natural_language",
            "input": {
                "text": "I need a small AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50 GB storage. Keep the monthly cost low."
            }
        }

        form_res = normalize_request(form_payload)
        nl_res = normalize_request(nl_payload)

        self.assertEqual(form_res["normalized_request"], nl_res["normalized_request"])

    def test_validation_errors_form(self):
        """Verifies field-level error messages for invalid requirements."""
        payload = {
            "mode": "form",
            "input": {
                "provider": "unsupported_cloud",
                "vcpu_min": -4,
                "memory_gb_min": 0,
                "storage_gb_min": -50
            }
        }
        res = normalize_request(payload)
        self.assertTrue(res["needs_clarification"])
        self.assertGreater(len(res["errors"]), 0)
        self.assertIsNone(res["normalized_request"])

    def test_clarification_on_ambiguous_nl(self):
        """Verifies that incomplete natural language input triggers clarification rather than hallucinating."""
        payload = {
            "mode": "natural_language",
            "input": {"text": "I want a server with 16 GB RAM."}  # Missing provider, CPU, storage
        }
        res = normalize_request(payload)
        self.assertTrue(res["needs_clarification"])
        self.assertIsNotNone(res["clarification_prompt"])
        self.assertIn("Which cloud provider", res["clarification_prompt"])

    def test_dsl_synthesis_and_compiler_verification(self):
        """Verifies that normalized request produces CLARA DSL that compiles successfully."""
        nl_text = "I need an AWS web server in Mumbai with 4 vCPUs, 16 GB RAM, and 100 GB storage."
        res = normalize_request({"mode": "natural_language", "input": {"text": nl_text}})
        dsl = res.get("clara_dsl")
        self.assertIsNotNone(dsl)
        self.assertIn("CLOUD AWS", dsl)
        self.assertIn("REGION ap-south-1", dsl)
        self.assertIn("CPU 4", dsl)
        self.assertIn("MEMORY 16GB", dsl)
        self.assertIn("STORAGE 100GB", dsl)

        # Write to temporary file and execute clara.exe if available
        clara_bin = "./clara.exe" if os.name == "nt" else "./clara"
        if os.path.exists(clara_bin):
            tmp_path = "tests/normalization/tmp_generated.clara"
            with open(tmp_path, "w") as f:
                f.write(dsl)

            try:
                proc = subprocess.run([clara_bin, "--check", tmp_path], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, f"clara.exe failed on generated DSL: {proc.stderr}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
