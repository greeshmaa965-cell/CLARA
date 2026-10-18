"""CLARA Recommendation and Constraint-Aware Alternative Generation Package."""

from .engine import generate_alternatives
from .constraints import evaluate_candidate_constraints, diagnose_infeasible_conflicts

__all__ = [
    "generate_alternatives",
    "evaluate_candidate_constraints",
    "diagnose_infeasible_conflicts"
]
