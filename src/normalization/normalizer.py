"""CLARA Unified Dual-Mode Normalizer.
Routes between Natural Language and Form inputs, validates against canonical schema,
and synthesizes valid CLARA DSL code.
"""

import sys
import json
import argparse
from typing import Any

from .schema import SCHEMA_VERSION
from .form_normalizer import normalize_form_input
from .natural_language import normalize_natural_language


def canonical_to_clara_dsl(req: dict) -> str:
    """Generates valid CLARA DSL source code from a canonical request object."""
    if not req:
        return ""

    provider = req.get("provider", "aws").upper()
    region = req.get("region", "ap-south-1")
    workload = req.get("workload", "web_server")
    reqs = req.get("requirements", {})

    vcpu = reqs.get("vcpu_min", 2)
    memory_gb = int(reqs.get("memory_gb_min", 4))
    storage_gb = int(reqs.get("storage_gb_min", 50))

    if workload == "database":
        resource_block = f"""    DATABASE {workload} {{
        STORAGE {storage_gb}GB
    }}"""
    else:
        resource_block = f"""    SERVER {workload} {{
        CPU {vcpu}
        MEMORY {memory_gb}GB
        STORAGE {storage_gb}GB
    }}"""

    return f"""CLOUD {provider} {{
    REGION {region}

{resource_block}
}}"""


def normalize_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Unified entrypoint for CLARA request normalization.

    Supports API contracts:
    - { "mode": "natural_language", "input": { "text": "..." } }
    - { "mode": "form", "input": { "provider": "aws", ... } }
    - Direct dictionaries with "text" or form keys.
    """
    mode = payload.get("mode")

    if mode == "natural_language":
        inp = payload.get("input", {})
        text = inp.get("text", "") if isinstance(inp, dict) else str(inp)
        result = normalize_natural_language(text)
    elif mode == "form":
        form_data = payload.get("input", {})
        if not isinstance(form_data, dict):
            form_data = payload
        result = normalize_form_input(form_data)
    elif "text" in payload:
        result = normalize_natural_language(payload["text"])
    elif "provider" in payload or "vcpu_min" in payload:
        result = normalize_form_input(payload)
    else:
        # Ambiguous payload
        result = {
            "schema_version": SCHEMA_VERSION,
            "input_mode": "unknown",
            "normalized_request": None,
            "warnings": [],
            "errors": ["Unable to determine input mode. Specify 'mode': 'form' or 'mode': 'natural_language'."],
            "needs_clarification": True,
            "clarification_prompt": "Please specify whether you are submitting structured form data or a natural language request."
        }

    # Attach synthesized CLARA DSL code if normalization succeeded
    if result.get("normalized_request"):
        result["clara_dsl"] = canonical_to_clara_dsl(result["normalized_request"])
    else:
        result["clara_dsl"] = None

    return result


def main():
    parser = argparse.ArgumentParser(description="CLARA Dual-Mode Normalizer CLI")
    parser.add_argument("--mode", choices=["natural_language", "form"], help="Input mode")
    parser.add_argument("--text", type=str, help="Natural language requirement prompt")
    parser.add_argument("--form-json", type=str, help="JSON string representing form fields")
    parser.add_argument("--dsl-only", action="store_true", help="Print only generated CLARA DSL")

    args = parser.parse_args()

    if args.text:
        payload = {"mode": "natural_language", "input": {"text": args.text}}
    elif args.form_json:
        try:
            form_data = json.loads(args.form_json)
            payload = {"mode": "form", "input": form_data}
        except json.JSONDecodeError as e:
            print(f"Error parsing form JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = normalize_request(payload)

    if args.dsl_only:
        if result.get("clara_dsl"):
            print(result["clara_dsl"])
        else:
            print("Cannot generate DSL: normalization failed.", file=sys.stderr)
            sys.exit(1)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
