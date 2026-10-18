"""Natural Language Requirement Extractor for CLARA.
Extracts structured infrastructure constraints from unstructured natural-language requests.
"""

import re
from .schema import (
    SCHEMA_VERSION,
    normalize_provider,
    normalize_region,
    normalize_workload,
    normalize_priority,
    validate_canonical_request
)


def extract_provider(text: str) -> str | None:
    text_lower = text.lower()
    if re.search(r"\b(aws|amazon|amazon web services)\b", text_lower):
        return "aws"
    if re.search(r"\b(azure|microsoft azure)\b", text_lower):
        return "azure"
    if re.search(r"\b(gcp|google cloud|google)\b", text_lower):
        return "gcp"
    return None


def extract_workload(text: str) -> str:
    text_lower = text.lower()
    if re.search(r"\b(data\s*base|postgres|mysql|sql|db)\b", text_lower):
        return "database"
    if re.search(r"\b(api\s*(?:server)?|microservice|backend)\b", text_lower):
        return "api_server"
    if re.search(r"\b(worker|queue|background)\b", text_lower):
        return "worker"
    if re.search(r"\b(web\s*(?:server|app|site)?)\b", text_lower):
        return "web_server"
    return "web_server"


def extract_region(text: str, provider: str) -> str:
    text_lower = text.lower()
    # Region location names
    if "mumbai" in text_lower or "india" in text_lower:
        return normalize_region(provider, "mumbai")
    if "virginia" in text_lower or "us-east" in text_lower:
        return normalize_region(provider, "virginia")
    if "frankfurt" in text_lower or "germany" in text_lower:
        return normalize_region(provider, "frankfurt")
    if "singapore" in text_lower:
        return normalize_region(provider, "singapore")

    # Check for direct code e.g. ap-south-1
    code_match = re.search(r"\b([a-z]{2}-[a-z]+-\d)\b", text_lower)
    if code_match:
        return code_match.group(1)

    return normalize_region(provider, "mumbai")


def extract_vcpu(text: str) -> int | None:
    # Matches: '2 vCPUs', '4 cores', '8 vcpu', 'cpu 4', '4 cpu'
    patterns = [
        r"(\d+)\s*(?:vcpus?|cores?|vcpu)",
        r"(?:vcpu|cpu|cores?)\s*(?:of\s*|:\s*)?(\d+)",
        r"(\d+)\s*cpu\b"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def extract_memory_gb(text: str) -> float | None:
    # Matches: '4 GB RAM', '16GB memory', '8192 MB ram', 'RAM 8 GB'
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(gb|mb|tb)\s*(?:ram|memory)?",
        r"(?:ram|memory)\s*(?:of\s*|:\s*)?(\d+(?:\.\d+)?)\s*(gb|mb|tb)"
    ]
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            val = float(m.group(1))
            unit = m.group(2).upper()
            if unit == "MB":
                return val / 1024.0
            if unit == "TB":
                return val * 1024.0
            return val
    return None


def extract_storage_gb(text: str) -> float | None:
    # Matches: '50 GB storage', '100GB disk', '500 GB ssd', 'storage 200 GB'
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(gb|mb|tb)\s*(?:storage|disk|ssd|hdd|volume|space)",
        r"(?:storage|disk|ssd|hdd|volume|space)\s*(?:of\s*|:\s*)?(\d+(?:\.\d+)?)\s*(gb|mb|tb)"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            unit = m.group(2).upper()
            if unit == "MB":
                return val / 1024.0
            if unit == "TB":
                return val * 1024.0
            return val

    # Fallback: find second numeric quantity if text has two units
    quantities = list(re.finditer(r"(\d+(?:\.\d+)?)\s*(gb|mb|tb)", text, re.IGNORECASE))
    if len(quantities) >= 2:
        # Second quantity is usually storage
        m = quantities[1]
        val = float(m.group(1))
        unit = m.group(2).upper()
        if unit == "MB":
            return val / 1024.0
        if unit == "TB":
            return val * 1024.0
        return val

    return None


def extract_priority(text: str) -> str:
    text_lower = text.lower()
    if re.search(r"\b(low\s*cost|lowest\s*cost|cheap(?:est)?|cost\s*low|cost-optimized|save\s*money)\b", text_lower):
        return "cost"
    if re.search(r"\b(high\s*performance|fast(?:est)?|maximum\s*throughput|speed)\b", text_lower):
        return "performance"
    if re.search(r"\b(balanced|standard|moderate)\b", text_lower):
        return "balanced"
    return "cost"


def extract_budget(text: str) -> float | None:
    # Matches: '$50', '$ 100/month', 'budget of 75 USD'
    m = re.search(r"\$\s*(\d+(?:\.\d+)?)", text)
    if m:
        return float(m.group(1))
    m = re.search(r"budget\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*(?:usd|dollars)?", text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def normalize_natural_language(text: str) -> dict:
    """Extracts canonical requirements from natural-language text.
    Triggers clarification when required fields are missing or ambiguous.
    """
    errors = []
    warnings = []

    if not text or not text.strip():
        return {
            "schema_version": SCHEMA_VERSION,
            "input_mode": "natural_language",
            "normalized_request": None,
            "warnings": ["Empty input text provided."],
            "errors": ["Input text cannot be empty."],
            "needs_clarification": True,
            "clarification_prompt": "Please describe your cloud infrastructure requirements (e.g., provider, CPU, memory, and storage)."
        }

    provider = extract_provider(text)
    if not provider:
        return {
            "schema_version": SCHEMA_VERSION,
            "input_mode": "natural_language",
            "normalized_request": None,
            "warnings": warnings,
            "errors": ["Could not determine cloud provider from input."],
            "needs_clarification": True,
            "clarification_prompt": "Which cloud provider would you like to use: AWS, Azure, or GCP?"
        }

    workload = extract_workload(text)
    region = extract_region(text, provider)
    vcpu = extract_vcpu(text)
    memory_gb = extract_memory_gb(text)
    storage_gb = extract_storage_gb(text)
    priority = extract_priority(text)
    budget = extract_budget(text)

    # Check for missing core dimensions
    missing = []
    if vcpu is None:
        missing.append("CPU/vCPU count")
    if memory_gb is None:
        missing.append("Memory/RAM capacity")
    if storage_gb is None:
        missing.append("Storage capacity")

    if missing:
        return {
            "schema_version": SCHEMA_VERSION,
            "input_mode": "natural_language",
            "normalized_request": None,
            "warnings": warnings,
            "errors": [f"Missing required specifications: {', '.join(missing)}."],
            "needs_clarification": True,
            "clarification_prompt": f"Please specify the following details for your {provider.upper()} {workload}: {', '.join(missing)}."
        }

    canonical_request = {
        "provider": provider,
        "workload": workload,
        "region": region,
        "requirements": {
            "vcpu_min": vcpu,
            "memory_gb_min": memory_gb,
            "storage_gb_min": storage_gb
        },
        "optimization": {
            "priority": priority,
            "monthly_budget": budget
        },
        "constraints": {
            "must_satisfy_all": True
        }
    }

    validation_errors = validate_canonical_request(canonical_request)
    if validation_errors:
        errors.extend(validation_errors)
        return {
            "schema_version": SCHEMA_VERSION,
            "input_mode": "natural_language",
            "normalized_request": None,
            "warnings": warnings,
            "errors": errors,
            "needs_clarification": True,
            "clarification_prompt": errors[0]
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "input_mode": "natural_language",
        "normalized_request": canonical_request,
        "warnings": warnings,
        "errors": [],
        "needs_clarification": False,
        "clarification_prompt": None
    }
