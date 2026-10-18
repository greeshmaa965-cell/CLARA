"""Normalizer for structured form inputs in CLARA."""

from .schema import (
    SCHEMA_VERSION,
    normalize_provider,
    normalize_region,
    normalize_workload,
    normalize_priority,
    validate_canonical_request
)


def normalize_form_input(form_data: dict) -> dict:
    """Normalizes structured dictionary/form data into canonical request JSON."""
    warnings = []
    errors = []

    raw_provider = form_data.get("provider")
    provider = normalize_provider(raw_provider)
    if not provider:
        errors.append(f"Invalid or missing provider '{raw_provider}'. Supported: AWS, Azure, GCP.")

    provider_clean = provider or "aws"
    raw_region = form_data.get("region", "")
    region = normalize_region(provider_clean, raw_region)

    workload = normalize_workload(form_data.get("workload", "web_server"))

    # Requirements
    try:
        vcpu_min = int(form_data.get("vcpu_min", form_data.get("cpu", 1)))
    except (ValueError, TypeError):
        vcpu_min = None
        errors.append("Invalid vcpu_min value. Must be a valid integer.")

    try:
        memory_gb_min = float(form_data.get("memory_gb_min", form_data.get("memory", 1.0)))
    except (ValueError, TypeError):
        memory_gb_min = None
        errors.append("Invalid memory_gb_min value. Must be a valid number.")

    try:
        storage_gb_min = float(form_data.get("storage_gb_min", form_data.get("storage", 10.0)))
    except (ValueError, TypeError):
        storage_gb_min = None
        errors.append("Invalid storage_gb_min value. Must be a valid number.")

    # Optimization
    priority = normalize_priority(form_data.get("optimization_priority", form_data.get("priority", "cost")))
    raw_budget = form_data.get("monthly_budget")
    monthly_budget = None
    if raw_budget is not None and str(raw_budget).strip():
        try:
            monthly_budget = float(raw_budget)
        except (ValueError, TypeError):
            errors.append("Invalid monthly_budget value. Must be a number or null.")

    canonical_request = {
        "provider": provider,
        "workload": workload,
        "region": region,
        "requirements": {
            "vcpu_min": vcpu_min,
            "memory_gb_min": memory_gb_min,
            "storage_gb_min": storage_gb_min
        },
        "optimization": {
            "priority": priority,
            "monthly_budget": monthly_budget
        },
        "constraints": {
            "must_satisfy_all": bool(form_data.get("must_satisfy_all", True))
        }
    }

    # Validate
    validation_errors = validate_canonical_request(canonical_request)
    errors.extend(validation_errors)

    return {
        "schema_version": SCHEMA_VERSION,
        "input_mode": "form",
        "normalized_request": canonical_request if not errors else None,
        "warnings": warnings,
        "errors": errors,
        "needs_clarification": bool(errors),
        "clarification_prompt": errors[0] if errors else None
    }
