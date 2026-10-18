"""Rule identifiers and explanation generators for CLARA Explainable Configuration Diff."""

RULE_WORKLOAD_MEMORY_HEADROOM = "WORKLOAD_MEMORY_HEADROOM"
RULE_WORKLOAD_CPU_HEADROOM = "WORKLOAD_CPU_HEADROOM"
RULE_INSTANCE_SHAPE_COUPLING = "INSTANCE_SHAPE_COUPLING"
RULE_STORAGE_ALIGNMENT = "STORAGE_ALIGNMENT"
RULE_INSTANCE_MAPPING = "INSTANCE_MAPPING"
RULE_COST_ESTIMATION = "COST_ESTIMATION"
RULE_EXACT_MATCH = "EXACT_MATCH"


def explain_vcpu_change(old_val: int, new_val: int, profile: str) -> tuple[str, str]:
    if old_val == new_val:
        return ("No change required: exact match with declared requirements.", RULE_EXACT_MATCH)
    if new_val > old_val:
        if profile == "performance_focused":
            return (
                f"Increased vCPU from {old_val} to {new_val} to deliver high compute throughput under concurrent traffic.",
                RULE_WORKLOAD_CPU_HEADROOM
            )
        if profile == "balanced":
            return (
                f"Increased vCPU from {old_val} to {new_val} to provide +100% capacity headroom for unexpected traffic spikes.",
                RULE_WORKLOAD_CPU_HEADROOM
            )
        return (
            f"Adjusted vCPU from {old_val} to {new_val} due to provider hardware instance shape constraints.",
            RULE_INSTANCE_SHAPE_COUPLING
        )
    return (f"Decreased vCPU from {old_val} to {new_val} to reduce unnecessary infrastructure costs.", RULE_INSTANCE_MAPPING)


def explain_memory_change(old_val: float, new_val: float, profile: str) -> tuple[str, str]:
    if old_val == new_val:
        return ("No change required: exact match with declared requirements.", RULE_EXACT_MATCH)
    if new_val > old_val:
        if profile == "performance_focused":
            return (
                f"Scaled memory from {old_val:.1f} GB to {new_val:.1f} GB to prevent out-of-memory errors during high-concurrency requests.",
                RULE_WORKLOAD_MEMORY_HEADROOM
            )
        if profile == "balanced":
            return (
                f"Allocated {new_val:.1f} GB RAM (up from {old_val:.1f} GB) to provide a comfortable operational buffer.",
                RULE_WORKLOAD_MEMORY_HEADROOM
            )
        return (
            f"Allocated {new_val:.1f} GB RAM to match the nearest standard provider instance shape.",
            RULE_INSTANCE_SHAPE_COUPLING
        )
    return (f"Adjusted memory from {old_val:.1f} GB to {new_val:.1f} GB.", RULE_INSTANCE_MAPPING)


def explain_storage_change(old_val: float, new_val: float) -> tuple[str, str]:
    if old_val == new_val:
        return ("No change required: exact match with declared requirements.", RULE_EXACT_MATCH)
    if new_val > old_val:
        return (
            f"Increased storage capacity from {old_val:.0f} GB to {new_val:.0f} GB to ensure adequate disk volume space.",
            RULE_STORAGE_ALIGNMENT
        )
    return (f"Adjusted storage from {old_val:.0f} GB to {new_val:.0f} GB.", RULE_STORAGE_ALIGNMENT)
