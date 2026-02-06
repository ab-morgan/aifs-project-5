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
    embeddings: List[Dict[str, Any]],
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    Compute top-k most similar job embeddings.

    Args:
        query_vector (List[float]): Resume embedding
        embeddings (List[Dict[str, Any]]): List of {job_id, embedding}
        top_k (int): Number of results to return

    Returns:
        List[Dict[str, Any]]: Sorted by similarity desc
    """
    if not embeddings:
        return []

    q = np.array(query_vector, dtype=float)

    sims = []
    for row in embeddings:
        job_id = row["job_id"]
        vec = np.array(row["embedding"], dtype=float)

        sim = cosine_similarity(q, vec)
        sims.append({"job_id": job_id, "similarity": sim})

    # Sort descending by similarity
    sims.sort(key=lambda x: x["similarity"], reverse=True)

    return sims[:top_k]
