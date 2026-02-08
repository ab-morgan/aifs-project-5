"""
similarity.py

Provides similarity search utilities for comparing a resume embedding
against precomputed job embeddings.

This module is:
- Pure (no side effects)
- Vectorized (NumPy-based)
- Model-agnostic
- Multi-user safe

Functions:
- cosine_similarity(a, b)
- compute_top_k(query_vector, embeddings, top_k)
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict, Any

import json

def parse_embedding(value):
    """
    Ensures embeddings loaded from Supabase are converted into
    a list[float], even if stored as a JSON string.
    """
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid embedding string: {value[:50]}...")

    raise TypeError(f"Unexpected embedding type: {type(value)}")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        a (np.ndarray): Shape (D,)
        b (np.ndarray): Shape (D,)

    Returns:
        float: Cosine similarity
    """
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def compute_top_k(
    query_vector: List[float],
    job_vectors: List[np.ndarray],
    top_k: int = 10,
) -> List[Tuple[int, float]]:
    """
    Compute top-k most similar job embeddings.

    Args:
        query_vector (List[float]): Resume embedding
        job_vectors (List[np.ndarray]): List of embedding vectors
        top_k (int): Number of results to return

    Returns:
        List[Tuple[int, float]]: List of (index, similarity) sorted desc
    """
    if not job_vectors:
        return []

    q = np.array(query_vector, dtype=float)

    sims = []
    for idx, vec in enumerate(job_vectors):
        sim = cosine_similarity(q, vec)
        sims.append((idx, sim))

    # Sort descending by similarity
    sims.sort(key=lambda x: x[1], reverse=True)

    return sims[:top_k]
