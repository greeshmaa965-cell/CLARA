"""CLARA Explainable Configuration Diff Engine.
Calculates exact deltas between user requirements and recommended architectures,
attaching grounded justifications and rule IDs for every field.
Supports single-candidate itemized diffs and multi-candidate comparative matrices.
"""

import os
import sys
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


def compute_matrix_diff(original_request: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Computes a multi-candidate comparative diff matrix across all alternatives."""
    diffs = [compute_explainable_diff(original_request, cand, include_unchanged=True) for cand in candidates]
    reqs = original_request.get("requirements", {})

    matrix = {
        "original": {
            "vcpu": reqs.get("vcpu_min", 2),
            "memory_gb": float(reqs.get("memory_gb_min", 4.0)),
            "storage_gb": float(reqs.get("storage_gb_min", 20.0)),
            "instance_type": "None (User Defined)",
            "estimated_monthly_cost": "N/A"
        },
        "candidates": diffs
    }
    return matrix


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
    lines.append("\n" + "=" * 110)
    lines.append(f"CLARA CONFIGURATION DIFF | User Request vs. Candidate {cand_id} ({profile})")
    lines.append("=" * 110)
    lines.append(f"{'Field':<24} {'Original':<14} {'Recommended':<18} {'Action':<12} {'Explanation & Grounded Rule'}")
    lines.append("-" * 110)

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

    lines.append("=" * 110 + "\n")
    return "\n".join(lines)


def matrix_to_text(original_req: dict[str, Any], alt_result: dict[str, Any]) -> str:
    """Prints a multi-candidate side-by-side comparison matrix."""
    lines = []
    reqs = original_req.get("requirements", {})
    candidates = alt_result.get("candidates", [])

    lines.append("\n" + "=" * 110)
    lines.append("CLARA MULTI-CANDIDATE COMPARATIVE MATRIX & EXPLAINABLE DIFF")
    lines.append("=" * 110)

    header = f"{'Dimension':<18} {'Original':<16} " + " ".join([f"{c['candidate_id']} ({c['profile'].title()}):<24" for c in candidates])
    # Build columns
    cols = [f"{c['candidate_id']} ({c['profile'].replace('_', ' ').title()})" for c in candidates]
    lines.append(f"{'Dimension':<20} {'User Request':<18} " + "".join([f"{col:<24}" for col in cols]))
    lines.append("-" * 110)

    # vCPU row
    vcpu_row = f"{'vCPU Cores':<20} {str(reqs.get('vcpu_min', 2)) + ' cores':<18} "
    for c in candidates:
        vcpu_row += f"{str(c['resources']['vcpu']) + ' cores':<24}"
    lines.append(vcpu_row)

    # Memory row
    mem_row = f"{'Memory / RAM':<20} {str(reqs.get('memory_gb_min', 4.0)) + ' GB':<18} "
    for c in candidates:
        mem_row += f"{str(c['resources']['memory_gb']) + ' GB':<24}"
    lines.append(mem_row)

    # Storage row
    storage_row = f"{'Storage Disk':<20} {str(reqs.get('storage_gb_min', 20.0)) + ' GB':<18} "
    for c in candidates:
        storage_row += f"{str(c['resources']['storage_gb']) + ' GB':<24}"
    lines.append(storage_row)

    # Instance Type row
    inst_row = f"{'Instance Type':<20} {'[User Defined]':<18} "
    for c in candidates:
        inst_row += f"{c['instance_type']:<24}"
    lines.append(inst_row)

    # Monthly Cost row
    cost_row = f"{'Est. Monthly Cost':<20} {'[Unpriced]':<18} "
    for c in candidates:
        cost_row += f"{'$' + str(c['cost']['total_monthly']) + '/mo':<24}"
    lines.append(cost_row)

    lines.append("=" * 110 + "\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="CLARA Explainable Configuration Diff CLI")
    parser.add_argument("--original-json", type=str, help="Canonical original request JSON string")
    parser.add_argument("--candidate-json", type=str, help="Selected candidate configuration JSON string")
    parser.add_argument("--text", type=str, help="Natural language request (runs Phase 4 + Phase 5 + Phase 6)")
    parser.add_argument("--clara-file", type=str, help="Path to .clara DSL file to analyze")
    parser.add_argument("--candidate", type=str, default=None, help="Candidate ID to diff against (A, B, or C)")
    parser.add_argument("--matrix", action="store_true", help="Print side-by-side comparative matrix across all candidates")
    parser.add_argument("--markdown", action="store_true", help="Format output as Markdown table")
    parser.add_argument("--hide-unchanged", action="store_true", help="Exclude unchanged fields from diff")
    parser.add_argument("--export-json", type=str, help="Save diff output to JSON file")
    parser.add_argument("--export-md", type=str, help="Save diff output to Markdown file")

    args = parser.parse_args()

    orig = None
    cand = None
    alt_result = None

    if args.text:
        from src.normalization.normalizer import normalize_request
        from src.recommendations.engine import generate_alternatives

        norm_res = normalize_request({"mode": "natural_language", "input": {"text": args.text}})
        if norm_res.get("needs_clarification"):
            print(f"Clarification needed: {norm_res.get('clarification_prompt')}")
            return
        orig = norm_res["normalized_request"]
        alt_result = generate_alternatives(orig)

    elif args.clara_file:
        import subprocess
        from src.recommendations.engine import generate_alternatives

        clara_bin = "./clara.exe" if os.name == "nt" else "./clara"
        if not os.path.exists(clara_bin):
            print(f"Error: '{clara_bin}' not found. Please build the compiler first.")
            return

        proc = subprocess.run([clara_bin, "--ir", args.clara_file], capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"Error compiling '{args.clara_file}':\n{proc.stderr}")
            return

        ir_data = json.loads(proc.stdout)
        servers = ir_data.get("resources", {}).get("servers", [])
        vcpu = servers[0]["cpu"] if servers else 2
        mem = servers[0]["memory_gb"] if servers else 4.0
        storage = servers[0]["storage_gb"] if servers else 20.0

        orig = {
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
        alt_result = generate_alternatives(orig)

    elif args.original_json and args.candidate_json:
        try:
            orig = json.loads(args.original_json)
            cand = json.loads(args.candidate_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return
    else:
        parser.print_help()
        return

    # If alternatives were generated, pick selected or recommended candidate
    if alt_result is not None:
        if args.matrix:
            print(matrix_to_text(orig, alt_result))
            return

        candidates = alt_result.get("candidates", [])
        if args.candidate:
            cand = next((c for c in candidates if c["candidate_id"].upper() == args.candidate.upper()), candidates[0])
        else:
            rec_id = alt_result.get("recommended_candidate_id", "A")
            cand = next((c for c in candidates if c["candidate_id"] == rec_id), candidates[0])

    diff = compute_explainable_diff(orig, cand, include_unchanged=not args.hide_unchanged)

    if args.markdown:
        output = diff_to_markdown(diff, show_unchanged=not args.hide_unchanged)
    else:
        output = diff_to_text(diff, show_unchanged=not args.hide_unchanged)

    print(output)

    if args.export_json:
        with open(args.export_json, "w", encoding="utf-8") as f:
            json.dump(diff, f, indent=2)
        print(f"Wrote diff JSON to '{args.export_json}'")

    if args.export_md:
        md_text = diff_to_markdown(diff, show_unchanged=not args.hide_unchanged)
        with open(args.export_md, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"Wrote diff Markdown to '{args.export_md}'")


if __name__ == "__main__":
    main()
