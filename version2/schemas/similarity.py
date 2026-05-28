"""
similarity.py

Schema for similarity results returned by the similarity engine.
Used by:
- job_matching service
- runtime UI
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SimilarityResult:
    job_id: int
    similarity: float
