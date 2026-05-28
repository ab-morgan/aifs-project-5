"""
seniority_normalization.py

Provides utilities to normalize job seniority levels into a small,
consistent set of buckets (e.g., junior, mid, senior, lead).

This is useful for:
- analytics
- filtering
- mobility scoring
"""

from __future__ import annotations

from typing import Optional


SENIORITY_MAP = {
    "intern": "junior",
    "entry": "junior",
    "junior": "junior",
    "associate": "mid",
    "mid": "mid",
    "staff": "mid",
    "senior": "senior",
    "principal": "senior",
    "lead": "lead",
    "manager": "lead",
    "director": "lead",
}


def normalize_seniority(raw_title: Optional[str]) -> Optional[str]:
    """
    Normalize a raw job title or seniority string into a canonical bucket.

    Args:
        raw_title: Free-text job title or seniority phrase.

    Returns:
        str or None: One of {"junior", "mid", "senior", "lead"} or None.
    """
    if not raw_title:
        return None

    text = raw_title.lower()

    for key, bucket in SENIORITY_MAP.items():
        if key in text:
            return bucket

    return None
