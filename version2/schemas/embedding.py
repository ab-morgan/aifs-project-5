"""
embedding.py

Schema for job embeddings stored in Supabase.
Used by:
- compute_embeddings
- similarity engine
- caching service
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class JobEmbedding:
    job_id: int
    embedding: List[float]
