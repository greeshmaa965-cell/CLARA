"""CLARA Explainable Configuration Diff Engine.
Calculates exact deltas between user requirements and recommended architectures,
attaching grounded justifications and rule IDs for every field.
"""

import json
import argparse
from typing import Any

from .rules import (
    explain_vcpu_change,
    explain_memory_change,
    explain_storage_change,
    RULE_INSTANCE_MAPPING,
    RULE_COST_ESTIMATION,
    RULE_EXACT_MATCH
)


def compute_explainable_diff(
    original_request: dict[str, Any],
    candidate: dict[str, Any],
    include_unchanged: bool = True
) -> dict[str, Any]:
    """Computes an itemized explainable diff between user requirements and a selected candidate."""
    reqs = original_request.get("requirements", {})
    cand_res = candidate.get("resources", {})
    profile = candidate.get("profile", "balanced")
    cand_id = candidate.get("candidate_id", "A")

    orig_vcpu = reqs.get("vcpu_min", 2)
    new_vcpu = cand_res.get("vcpu", orig_vcpu)

    orig_mem = float(reqs.get("memory_gb_min", 4.0))
    new_mem = float(cand_res.get("memory_gb", orig_mem))

    orig_storage = float(reqs.get("storage_gb_min", 20.0))
    new_storage = float(cand_res.get("storage_gb", orig_storage))

    changes = []
    unchanged = []

    # 1. vCPU Comparison
    reason, rule_id = explain_vcpu_change(orig_vcpu, new_vcpu, profile)
    if orig_vcpu != new_vcpu:
        changes.append({
            "field": "vcpu",
            "display_name": "vCPU Cores",
            "change_type": "modified",
            "old_value": orig_vcpu,
            "new_value": new_vcpu,
            "unit": "cores",
            "reason": reason,
            "rule_id": rule_id,
            "severity": "recommendation"
        })
    else:
        unchanged.append({
            "field": "vcpu",
            "display_name": "vCPU Cores",
            "value": orig_vcpu,
            "unit": "cores",
            "reason": reason,
            "rule_id": rule_id
        })

    # 2. Memory Comparison
    reason, rule_id = explain_memory_change(orig_mem, new_mem, profile)
    if orig_mem != new_mem:
        changes.append({
            "field": "memory_gb",
            "display_name": "Memory / RAM",
            "change_type": "modified",
            "old_value": orig_mem,
            "new_value": new_mem,
            "unit": "GB",
            "reason": reason,
            "rule_id": rule_id,
            "severity": "recommendation"
        })
    else:
        unchanged.append({
            "field": "memory_gb",
            "display_name": "Memory / RAM",
            "value": orig_mem,
            "unit": "GB",
            "reason": reason,
            "rule_id": rule_id
        })

    # 3. Storage Comparison
    reason, rule_id = explain_storage_change(orig_storage, new_storage)
    if orig_storage != new_storage:
        changes.append({
            "field": "storage_gb",
            "display_name": "Storage Disk",
            "change_type": "modified",
            "old_value": orig_storage,
            "new_value": new_storage,
            "unit": "GB",
            "reason": reason,
            "rule_id": rule_id,
            "severity": "recommendation"
        })
    else:
        unchanged.append({
            "field": "storage_gb",
            "display_name": "Storage Disk",
            "value": orig_storage,
            "unit": "GB",
            "reason": reason,
            "rule_id": rule_id
        })

    # 4. Added Architectural Details
    added_fields = []
    if "instance_type" in candidate:
        added_fields.append({
            "field": "instance_type",
            "display_name": "Instance Hardware Type",
            "change_type": "added",
            "old_value": None,
            "new_value": candidate["instance_type"],
            "unit": None,
            "reason": f"Selected provider hardware offering '{candidate['instance_type']}' to fulfill required resources.",
            "rule_id": RULE_INSTANCE_MAPPING,
            "severity": "info"
        })

    if "cost" in candidate:
        total_monthly = candidate["cost"]["total_monthly"]
        currency = candidate["cost"].get("currency", "USD")
        added_fields.append({
            "field": "estimated_monthly_cost",
            "display_name": "Estimated Monthly Cost",
            "change_type": "added",
            "old_value": None,
            "new_value": f"${total_monthly:.2f} {currency}/mo",
            "unit": currency,
            "reason": f"Calculated based on {candidate['instance_type']} compute rate + {new_storage:.0f} GB storage.",
            "rule_id": RULE_COST_ESTIMATION,
            "severity": "info"
        })

    all_changes = changes + added_fields

    diff_result = {
        "original_candidate_id": "user_configuration",
        "recommended_candidate_id": cand_id,
        "profile": profile,
        "summary": {
            "total_changes": len(all_changes),
            "modified_fields": len(changes),
            "added_fields": len(added_fields),
            "unchanged_fields": len(unchanged)
        },
        "changes": all_changes
    }

    if include_unchanged:
        diff_result["unchanged"] = unchanged

    return diff_result


def diff_to_markdown(diff: dict[str, Any], show_unchanged: bool = True) -> str:
    """Formats the explainable diff as a GitHub Flavored Markdown table."""
    lines = []
    cand_id = diff.get("recommended_candidate_id", "A")
    profile = diff.get("profile", "balanced").replace("_", " ").title()
    lines.append(f"### Configuration Diff: User Request vs. Candidate {cand_id} ({profile})\n")
    lines.append("| Field | Original | Recommended | Action | Explanation & Rule |")
    lines.append("|---|---|---|---|---|")

    for c in diff.get("changes", []):
        field = c["display_name"]
        old_val = f"{c['old_value']} {c['unit'] or ''}".strip() if c["old_value"] is not None else "—"
        new_val = f"{c['new_value']} {c['unit'] or ''}".strip()
        action = f"**{c['change_type'].upper()}**"
        reason = f"{c['reason']} (`{c['rule_id']}`)"
        lines.append(f"| {field} | {old_val} | {new_val} | {action} | {reason} |")

    if show_unchanged:
        for u in diff.get("unchanged", []):
            field = u["display_name"]
            val = f"{u['value']} {u['unit'] or ''}".strip()
            lines.append(f"| {field} | {val} | {val} | UNCHANGED | {u['reason']} |")

    return "\n".join(lines)


def diff_to_text(diff: dict[str, Any], show_unchanged: bool = True) -> str:
    """Formats the explainable diff as a clean ASCII comparison table."""
    lines = []
    cand_id = diff.get("recommended_candidate_id", "A")
    profile = diff.get("profile", "balanced").replace("_", " ").title()
    lines.append("\n" + "=" * 108)
    lines.append(f"CLARA CONFIGURATION DIFF | User Request vs. Candidate {cand_id} ({profile})")
    lines.append("=" * 108)
    lines.append(f"{'Field':<24} {'Original':<14} {'Recommended':<18} {'Action':<12} {'Explanation & Grounded Rule'}")
    lines.append("-" * 108)

    for c in diff.get("changes", []):
        field = c["display_name"]
        old_val = f"{c['old_value']} {c['unit'] or ''}".strip() if c["old_value"] is not None else "—"
        new_val = f"{c['new_value']} {c['unit'] or ''}".strip()
        action = c["change_type"].upper()
        reason = f"{c['reason']} [{c['rule_id']}]"
        lines.append(f"{field:<24} {old_val:<14} {new_val:<18} {action:<12} {reason}")

    if show_unchanged:
        for u in diff.get("unchanged", []):
            field = u["display_name"]
            val = f"{u['value']} {u['unit'] or ''}".strip()
            lines.append(f"{field:<24} {val:<14} {val:<18} {'UNCHANGED':<12} {u['reason']}")

    lines.append("=" * 108 + "\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="CLARA Explainable Configuration Diff CLI")
    parser.add_argument("--original-json", type=str, required=True, help="Canonical original request JSON string")
    parser.add_argument("--candidate-json", type=str, required=True, help="Selected candidate configuration JSON string")
    parser.add_argument("--markdown", action="store_true", help="Format output as Markdown table")
    parser.add_argument("--hide-unchanged", action="store_true", help="Exclude unchanged fields from diff")

    args = parser.parse_args()

    try:
        orig = json.loads(args.original_json)
        cand = json.loads(args.candidate_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    diff = compute_explainable_diff(orig, cand, include_unchanged=not args.hide_unchanged)

    if args.markdown:
        print(diff_to_markdown(diff, show_unchanged=not args.hide_unchanged))
    else:
        print(diff_to_text(diff, show_unchanged=not args.hide_unchanged))


if __name__ == "__main__":
    main()
