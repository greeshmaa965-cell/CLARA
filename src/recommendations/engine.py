"""CLARA Constraint-Aware Multi-Candidate Recommendation Engine.
Evaluates hardware catalogues, filters hard constraints, scores trade-offs,
and generates distinct alternatives (Cost-Optimized, Balanced, Performance-Focused).
"""

import os
import json
import argparse
from typing import Any

from .constraints import evaluate_candidate_constraints, diagnose_infeasible_conflicts

DEFAULT_CATALOG_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/resource_catalog/catalog_snapshot.json"
)


def load_catalog(path: str = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_alternatives(
    canonical_request: dict[str, Any],
    catalog_path: str = DEFAULT_CATALOG_PATH,
    request_id: str = "clara-req-001"
) -> dict[str, Any]:
    """Generates multiple feasible candidates and comparative trade-offs for a canonical request."""
    catalog = load_catalog(catalog_path)
    dataset_version = catalog.get("dataset_version", "pricing-snapshot-2026-10-18")
    currency = catalog.get("currency", "USD")

    provider = canonical_request.get("provider", "aws").lower()
    region = canonical_request.get("region", "ap-south-1")
    reqs = canonical_request.get("requirements", {})
    storage_gb = float(reqs.get("storage_gb_min", 20.0))
    optimization = canonical_request.get("optimization", {})
    priority = optimization.get("priority", "cost")
    budget = optimization.get("monthly_budget")

    provider_data = catalog["providers"].get(provider)
    if not provider_data:
        return {
            "request_id": request_id,
            "dataset_version": dataset_version,
            "status": "ERROR",
            "message": f"Provider '{provider}' not found in catalogue.",
            "candidates": []
        }

    storage_price = provider_data.get("storage_price_per_gb_month", 0.08)
    instances = provider_data.get("instances", [])

    # Evaluate each instance against hard constraints
    evaluated_instances = []
    feasible_candidates = []

    for inst in instances:
        eval_res = evaluate_candidate_constraints(inst, storage_gb, storage_price, reqs, budget)
        eval_res["instance"] = inst
        evaluated_instances.append(eval_res)
        if eval_res["feasible"]:
            feasible_candidates.append(eval_res)

    # Infeasible diagnosis if 0 candidates pass
    if not feasible_candidates:
        diagnosis = diagnose_infeasible_conflicts(provider, instances, storage_price, reqs, budget)
        return {
            "request_id": request_id,
            "dataset_version": dataset_version,
            "status": "INFEASIBLE",
            "message": diagnosis["message"],
            "conflict_diagnosis": diagnosis,
            "candidates": []
        }

    # Sort feasible by cost
    feasible_candidates.sort(key=lambda x: (x["total_monthly_cost"], -x["instance"]["vcpu"]))

    # Pick 3 distinct candidates across the feasible spectrum:
    # 1. Cost-optimized: lowest cost meeting requirements
    cand_cost = feasible_candidates[0]

    # 2. Performance-focused: top capacity within budget
    cand_perf = feasible_candidates[-1]

    # 3. Balanced: median candidate between cost and perf
    mid_idx = len(feasible_candidates) // 2
    cand_balanced = feasible_candidates[mid_idx]

    # Format into structured alternatives
    candidates_list = []

    # Candidate A: Cost-Optimized
    candidates_list.append({
        "candidate_id": "A",
        "profile": "cost_optimized",
        "feasible": True,
        "instance_type": cand_cost["instance"]["type"],
        "family": cand_cost["instance"].get("family", "burstable"),
        "resources": {
            "vcpu": cand_cost["instance"]["vcpu"],
            "memory_gb": cand_cost["instance"]["memory_gb"],
            "storage_gb": cand_cost["actual_storage_gb"]
        },
        "cost": {
            "compute_monthly": cand_cost["compute_cost"],
            "storage_monthly": cand_cost["storage_cost"],
            "total_monthly": cand_cost["total_monthly_cost"],
            "currency": currency
        },
        "capacity_summary": "Meets declared minimum requirements with lowest resource cost.",
        "performance_summary": "Baseline compute; ideal for developmental, low-traffic, or cost-sensitive workloads.",
        "tradeoff_notes": "Lowest price point, but lower headroom for bursty load spikes.",
        "constraint_results": cand_cost["constraint_results"]
    })

    # Candidate B: Balanced
    # Only add if distinct from A, or adjust label
    b_id = "B"
    candidates_list.append({
        "candidate_id": b_id,
        "profile": "balanced",
        "feasible": True,
        "instance_type": cand_balanced["instance"]["type"],
        "family": cand_balanced["instance"].get("family", "general_purpose"),
        "resources": {
            "vcpu": cand_balanced["instance"]["vcpu"],
            "memory_gb": cand_balanced["instance"]["memory_gb"],
            "storage_gb": cand_balanced["actual_storage_gb"]
        },
        "cost": {
            "compute_monthly": cand_balanced["compute_cost"],
            "storage_monthly": cand_balanced["storage_cost"],
            "total_monthly": cand_balanced["total_monthly_cost"],
            "currency": currency
        },
        "capacity_summary": "Balanced headroom: provides +50% to +100% compute/RAM buffer for unexpected traffic.",
        "performance_summary": "Stable, predictable latency with dedicated resources for standard production services.",
        "tradeoff_notes": "Optimal balance of budget and capacity headroom.",
        "constraint_results": cand_balanced["constraint_results"]
    })

    # Candidate C: Performance-Focused
    c_id = "C"
    candidates_list.append({
        "candidate_id": c_id,
        "profile": "performance_focused",
        "feasible": True,
        "instance_type": cand_perf["instance"]["type"],
        "family": cand_perf["instance"].get("family", "compute_optimized"),
        "resources": {
            "vcpu": cand_perf["instance"]["vcpu"],
            "memory_gb": cand_perf["instance"]["memory_gb"],
            "storage_gb": cand_perf["actual_storage_gb"]
        },
        "cost": {
            "compute_monthly": cand_perf["compute_cost"],
            "storage_monthly": cand_perf["storage_cost"],
            "total_monthly": cand_perf["total_monthly_cost"],
            "currency": currency
        },
        "capacity_summary": "Maximum headroom: highest compute power and memory capacity among feasible candidates.",
        "performance_summary": "High-throughput and low-latency response times under high concurrency.",
        "tradeoff_notes": "Highest monthly cost, but delivers superior performance and scalability.",
        "constraint_results": cand_perf["constraint_results"]
    })

    # Rank candidates according to user optimization priority
    if priority == "performance":
        candidates_list.sort(key=lambda c: (-c["resources"]["vcpu"], -c["resources"]["memory_gb"]))
    elif priority == "balanced":
        # Put balanced first, then cost, then perf
        order = {"balanced": 0, "cost_optimized": 1, "performance_focused": 2}
        candidates_list.sort(key=lambda c: order.get(c["profile"], 3))
    else:  # "cost"
        candidates_list.sort(key=lambda c: c["cost"]["total_monthly"])

    return {
        "request_id": request_id,
        "dataset_version": dataset_version,
        "status": "SUCCESS",
        "optimization_priority": priority,
        "provider": provider,
        "region": region,
        "total_feasible_count": len(feasible_candidates),
        "recommended_candidate_id": candidates_list[0]["candidate_id"],
        "candidates": candidates_list
    }


def format_candidates_table(result: dict[str, Any]) -> str:
    """Formats candidate alternatives as a clean readable ASCII comparison table."""
    if result.get("status") != "SUCCESS":
        return f"Status: {result.get('status')}\nMessage: {result.get('message', 'No details available')}"

    lines = []
    lines.append("\n" + "=" * 96)
    lines.append(f"CLARA FEASIBLE ALTERNATIVES | Provider: {result['provider'].upper()} | Region: {result['region']}")
    lines.append(f"Dataset Version: {result['dataset_version']} | Priority: {result['optimization_priority'].upper()}")
    lines.append("=" * 96)
    lines.append(f"{'Profile':<22} {'ID':<4} {'Instance Type':<16} {'vCPU':<6} {'RAM':<10} {'Storage':<10} {'Est. Cost':<12} {'Trade-off'}")
    lines.append("-" * 96)

    for c in result["candidates"]:
        prof = c["profile"].replace("_", " ").title()
        cid = c["candidate_id"]
        rec_mark = " (RECOMMENDED)" if cid == result.get("recommended_candidate_id") else ""
        prof_str = f"{prof}{rec_mark}"
        itype = c["instance_type"]
        vcpu = f"{c['resources']['vcpu']} core"
        ram = f"{c['resources']['memory_gb']:.1f} GB"
        storage = f"{c['resources']['storage_gb']:.0f} GB"
        cost = f"${c['cost']['total_monthly']:.2f}/mo"
        tradeoff = c["tradeoff_notes"]

        lines.append(f"{prof_str:<22} {cid:<4} {itype:<16} {vcpu:<6} {ram:<10} {storage:<10} {cost:<12} {tradeoff}")

    lines.append("=" * 96 + "\n")
    return "\n".join(lines)


def main():
    import subprocess
    parser = argparse.ArgumentParser(description="CLARA Alternative Generation Engine")
    parser.add_argument("--request-json", type=str, help="Canonical request JSON string")
    parser.add_argument("--clara-file", type=str, help="Path to .clara DSL file to analyze")
    parser.add_argument("--catalog", type=str, default=DEFAULT_CATALOG_PATH, help="Path to catalog snapshot")
    parser.add_argument("--summary", action="store_true", help="Print human-readable comparison table")

    args = parser.parse_args()

    req = None
    if args.request_json:
        try:
            req = json.loads(args.request_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing request JSON: {e}")
            return
    elif args.clara_file:
        clara_bin = "./clara.exe" if os.name == "nt" else "./clara"
        if not os.path.exists(clara_bin):
            print(f"Error: '{clara_bin}' not found. Please build the compiler first using scripts/build.ps1 or build.sh.")
            return

        proc = subprocess.run([clara_bin, "--ir", args.clara_file], capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"Error running compiler on '{args.clara_file}':\n{proc.stderr}")
            return

        try:
            ir_data = json.loads(proc.stdout)
            servers = ir_data.get("resources", {}).get("servers", [])
            vcpu = servers[0]["cpu"] if servers else 2
            mem = servers[0]["memory_gb"] if servers else 4.0
            storage = servers[0]["storage_gb"] if servers else 20.0

            req = {
                "provider": ir_data.get("provider", "aws"),
                "region": ir_data.get("region", "ap-south-1"),
                "workload": servers[0]["name"] if servers else "web_server",
                "requirements": {
                    "vcpu_min": vcpu,
                    "memory_gb_min": mem,
                    "storage_gb_min": storage
                },
                "optimization": {"priority": "cost", "monthly_budget": None},
                "constraints": {"must_satisfy_all": True}
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing compiler IR output: {e}\nRaw output:\n{proc.stdout}")
            return
    else:
        parser.print_help()
        return

    result = generate_alternatives(req, catalog_path=args.catalog)
    if args.summary:
        print(format_candidates_table(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
