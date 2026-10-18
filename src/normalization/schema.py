"""Canonical schema definitions, provider mappings, and validation rules for CLARA."""

SCHEMA_VERSION = "1.0"

SUPPORTED_PROVIDERS = {"aws", "azure", "gcp"}

SUPPORTED_WORKLOADS = {
    "web_server": "web_server",
    "web": "web_server",
    "web server": "web_server",
    "web app": "web_server",
    "database": "database",
    "db": "database",
    "sql": "database",
    "postgres": "database",
    "mysql": "database",
    "api": "api_server",
    "api_server": "api_server",
    "worker": "worker",
    "compute": "web_server"
}

SUPPORTED_PRIORITIES = {"cost", "performance", "balanced"}

# Canonical region mappings across providers
REGION_MAP = {
    "aws": {
        "mumbai": "ap-south-1",
        "ap-south-1": "ap-south-1",
        "virginia": "us-east-1",
        "us-east-1": "us-east-1",
        "frankfurt": "eu-central-1",
        "eu-central-1": "eu-central-1",
        "singapore": "ap-southeast-1",
        "ap-southeast-1": "ap-southeast-1"
    },
    "azure": {
        "mumbai": "centralindia",
        "centralindia": "centralindia",
        "india": "centralindia",
        "virginia": "eastus",
        "eastus": "eastus",
        "europe": "westeurope",
        "westeurope": "westeurope"
    },
    "gcp": {
        "mumbai": "asia-south1",
        "asia-south1": "asia-south1",
        "us": "us-central1",
        "us-central1": "us-central1",
        "frankfurt": "europe-west3",
        "europe-west3": "europe-west3"
    }
}


def normalize_provider(raw_provider: str) -> str | None:
    if not raw_provider:
        return None
    p = raw_provider.strip().lower()
    if p in {"aws", "amazon", "amazon web services"}:
        return "aws"
    if p in {"azure", "microsoft azure"}:
        return "azure"
    if p in {"gcp", "google", "google cloud", "google cloud platform"}:
        return "gcp"
    return p if p in SUPPORTED_PROVIDERS else None


def normalize_region(provider: str, raw_region: str) -> str:
    if not raw_region:
        return "ap-south-1" if provider == "aws" else ("centralindia" if provider == "azure" else "asia-south1")
    r = raw_region.strip().lower()
    mapping = REGION_MAP.get(provider, {})
    return mapping.get(r, raw_region.strip())


def normalize_workload(raw_workload: str) -> str:
    if not raw_workload:
        return "web_server"
    w = raw_workload.strip().lower()
    return SUPPORTED_WORKLOADS.get(w, "web_server")


def normalize_priority(raw_priority: str) -> str:
    if not raw_priority:
        return "cost"
    p = raw_priority.strip().lower()
    if p in {"low cost", "lowest cost", "cheapest", "cost-optimized", "cheap", "cost"}:
        return "cost"
    if p in {"performance", "fastest", "high performance", "speed", "throughput"}:
        return "performance"
    if p in {"balanced", "medium", "standard"}:
        return "balanced"
    return p if p in SUPPORTED_PRIORITIES else "cost"


def validate_canonical_request(req: dict) -> list[str]:
    """Validates canonical request fields and returns a list of error strings."""
    errors = []

    provider = req.get("provider")
    if not provider or provider not in SUPPORTED_PROVIDERS:
        errors.append(f"Invalid or unsupported provider '{provider}'. Must be one of {sorted(SUPPORTED_PROVIDERS)}.")

    workload = req.get("workload")
    if not workload:
        errors.append("Missing required field 'workload'.")

    requirements = req.get("requirements", {})
    vcpu = requirements.get("vcpu_min")
    if vcpu is None or not isinstance(vcpu, (int, float)) or vcpu <= 0:
        errors.append("Field 'requirements.vcpu_min' must be a positive number (> 0).")

    memory = requirements.get("memory_gb_min")
    if memory is None or not isinstance(memory, (int, float)) or memory <= 0:
        errors.append("Field 'requirements.memory_gb_min' must be a positive number (> 0).")

    storage = requirements.get("storage_gb_min")
    if storage is None or not isinstance(storage, (int, float)) or storage <= 0:
        errors.append("Field 'requirements.storage_gb_min' must be a positive number (> 0).")

    optimization = req.get("optimization", {})
    priority = optimization.get("priority")
    if priority and priority not in SUPPORTED_PRIORITIES:
        errors.append(f"Invalid optimization priority '{priority}'. Must be one of {sorted(SUPPORTED_PRIORITIES)}.")

    monthly_budget = optimization.get("monthly_budget")
    if monthly_budget is not None and (not isinstance(monthly_budget, (int, float)) or monthly_budget <= 0):
        errors.append("Field 'optimization.monthly_budget' must be a positive number if specified.")

    return errors
