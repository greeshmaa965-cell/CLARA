"""Constraint evaluation engine for CLARA candidate configurations.
Enforces hard constraints, produces audit results, and diagnoses infeasibility.
"""

from typing import Any


def evaluate_candidate_constraints(
    instance: dict[str, Any],
    storage_gb: float,
    storage_price_per_gb: float,
    reqs: dict[str, Any],
    budget: float | None
) -> dict[str, Any]:
    """Evaluates whether an instance + storage satisfies declared hard constraints."""
    constraint_results = []
    exclusion_reasons = []

    # vCPU check
    vcpu_min = reqs.get("vcpu_min", 1)
    vcpu_passed = instance["vcpu"] >= vcpu_min
    constraint_results.append({
        "constraint": f"vCPU >= {vcpu_min}",
        "actual": f"{instance['vcpu']} vCPU",
        "passed": vcpu_passed
    })
    if not vcpu_passed:
        exclusion_reasons.append(f"Insufficient vCPU: candidate provides {instance['vcpu']}, requires >= {vcpu_min}")

    # Memory check
    mem_min = reqs.get("memory_gb_min", 1.0)
    mem_passed = instance["memory_gb"] >= mem_min
    constraint_results.append({
        "constraint": f"Memory >= {mem_min} GB",
        "actual": f"{instance['memory_gb']} GB",
        "passed": mem_passed
    })
    if not mem_passed:
        exclusion_reasons.append(f"Insufficient RAM: candidate provides {instance['memory_gb']} GB, requires >= {mem_min} GB")

    # Storage check
    storage_min = reqs.get("storage_gb_min", 10.0)
    actual_storage = max(storage_gb, storage_min)
    storage_passed = actual_storage >= storage_min
    constraint_results.append({
        "constraint": f"Storage >= {storage_min} GB",
        "actual": f"{actual_storage} GB",
        "passed": storage_passed
    })

    # Cost calculation
    compute_cost = instance["monthly_rate"]
    storage_cost = actual_storage * storage_price_per_gb
    total_monthly_cost = round(compute_cost + storage_cost, 2)

    # Budget check
    if budget is not None and budget > 0:
        budget_passed = total_monthly_cost <= budget
        constraint_results.append({
            "constraint": f"Monthly Cost <= ${budget:.2f}",
            "actual": f"${total_monthly_cost:.2f}",
            "passed": budget_passed
        })
        if not budget_passed:
            exclusion_reasons.append(f"Exceeds budget ceiling: monthly cost ${total_monthly_cost:.2f} > limit ${budget:.2f}")

    feasible = len(exclusion_reasons) == 0

    return {
        "feasible": feasible,
        "actual_storage_gb": actual_storage,
        "compute_cost": round(compute_cost, 2),
        "storage_cost": round(storage_cost, 2),
        "total_monthly_cost": total_monthly_cost,
        "constraint_results": constraint_results,
        "exclusion_reasons": exclusion_reasons
    }


def diagnose_infeasible_conflicts(
    provider: str,
    instances: list[dict[str, Any]],
    storage_price_per_gb: float,
    reqs: dict[str, Any],
    budget: float | None
) -> dict[str, Any]:
    """Diagnoses why no candidate is feasible in the given catalogue."""
    vcpu_min = reqs.get("vcpu_min", 1)
    mem_min = reqs.get("memory_gb_min", 1.0)
    storage_min = reqs.get("storage_gb_min", 10.0)

    # Find the lowest cost instance that meets CPU + RAM ignoring budget
    min_viable_instance = None
    lowest_cost = float("inf")

    for inst in instances:
        if inst["vcpu"] >= vcpu_min and inst["memory_gb"] >= mem_min:
            t_cost = inst["monthly_rate"] + (storage_min * storage_price_per_gb)
            if t_cost < lowest_cost:
                lowest_cost = t_cost
                min_viable_instance = inst

    if min_viable_instance is not None and budget is not None and lowest_cost > budget:
        return {
            "conflict_type": "BUDGET_EXCEEDED",
            "message": (
                f"Declared monthly budget of ${budget:.2f} is insufficient. "
                f"The minimum feasible configuration on {provider.upper()} ({min_viable_instance['type']} with "
                f"{min_viable_instance['vcpu']} vCPU, {min_viable_instance['memory_gb']} GB RAM, {storage_min} GB storage) "
                f"costs approximately ${lowest_cost:.2f}/month."
            ),
            "suggested_budget": round(lowest_cost, 2),
            "suggested_instance": min_viable_instance["type"]
        }

    return {
        "conflict_type": "RESOURCE_UNAVAILABLE",
        "message": (
            f"No single instance in the {provider.upper()} catalogue satisfies the minimum requirements "
            f"({vcpu_min} vCPU, {mem_min} GB RAM). Consider distributing across multiple instances."
        ),
        "suggested_budget": None,
        "suggested_instance": None
    }
