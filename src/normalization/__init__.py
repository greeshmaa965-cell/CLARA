"""CLARA Dual-Mode Normalization Package.
Provides canonical JSON normalization for both Natural Language queries and Form inputs.
"""

from .normalizer import normalize_request, canonical_to_clara_dsl

__all__ = ["normalize_request", "canonical_to_clara_dsl"]
