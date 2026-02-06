"""
mobility_scoring.py

Provides utilities to score "mobility" between a candidate's current
role and a target job, based on:

- similarity score
- seniority delta
- optional job family match

This is intended for future analytics and UI features (e.g., "stretch"
roles vs. "lateral" moves).
"""

from __future__ import annotations

from typing import Optional


def compute_mobility_score(
    similarity: float,
    current_seniority: Optional[str],
    target_seniority: Optional[str],
    same_family: bool = True,
) -> float:
    """
    Compute a simple mobility score.

    Heuristics:
    - Base on similarity (0–1)
    - Penalize large seniority jumps
    - Slight bonus if same job family

    Args:
        similarity: Cosine similarity between resume and job.
        current_seniority: Canonical seniority bucket for candidate.
        target_seniority: Canonical seniority bucket for job.
        same_family: Whether job is in same job family.

    Returns:
        float: Mobility score (0–1+), higher is "better fit".
    """
    base = max(0.0, min(1.0, similarity))

    # Seniority penalty
    penalty = _seniority_penalty(current_seniority, target_seniority)
    score = base * (1.0 - penalty)

    # Bonus for same family
    if same_family:
        score *= 1.05

    return float(max(0.0, min(1.2, score)))  # cap slightly above 1 for bonus


SENIORITY_ORDER = ["junior", "mid", "senior", "lead"]


def _seniority_penalty(
    current: Optional[str],
    target: Optional[str],
) -> float:
    """
    Compute a penalty based on seniority gap.

    - 0 gap -> 0 penalty
    - 1 level up -> small penalty
    - 2+ levels up -> larger penalty
    """
    if current not in SENIORITY_ORDER or target not in SENIORITY_ORDER:
        return 0.0

    ci = SENIORITY_ORDER.index(current)
    ti = SENIORITY_ORDER.index(target)
    delta = ti - ci  # positive = moving up

    if delta <= 0:
        return 0.0
    if delta == 1:
        return 0.15
    if delta == 2:
        return 0.3
    return 0.5
