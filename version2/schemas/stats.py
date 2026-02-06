"""
stats.py

Schema for global embedding statistics computed during PREP.
Used by:
- compute_stats
- stats_service
- Streamlit sidebar
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class EmbeddingStats:
    mean: float
    std: float
    min: float
    max: float
