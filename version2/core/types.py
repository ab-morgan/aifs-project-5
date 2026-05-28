"""
types.py

Shared type aliases for clarity and consistency.
"""

from __future__ import annotations

from typing import Dict, List, Any, Tuple

Vector = List[float]
Matrix = List[List[float]]

EmbeddingRow = Dict[str, Any]      # {job_id, embedding}
JobRow = Dict[str, Any]            # {id, title, company, ...}
StatsRow = Dict[str, float]        # {mean, std, min, max}

SimilarityResult = Dict[str, float]  # {job_id, similarity}
