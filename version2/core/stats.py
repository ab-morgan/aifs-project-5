"""
stats.py

Pure statistical utilities used by the PREP pipeline and (later) by
runtime analytics. These functions operate on numpy arrays and return
simple Python types for easy serialization.

Functions included:
- compute_vector_norms(vectors)
- compute_embedding_distribution(vectors)
- compute_frequency_ranks(values)

All functions are pure, deterministic, and side-effect free.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any


def compute_vector_norms(vectors: np.ndarray) -> np.ndarray:
    """
    Compute the L2 norm for each embedding vector.

    Args:
        vectors (np.ndarray): Shape (N, D)

    Returns:
        np.ndarray: Shape (N,), containing the L2 norm of each vector.
    """
    if vectors.ndim != 2:
        raise ValueError("vectors must be a 2D numpy array")

    # L2 norm along axis 1
    norms = np.linalg.norm(vectors, axis=1)
    return norms


def compute_embedding_distribution(vectors: np.ndarray) -> Dict[str, float]:
    """
    Compute distribution statistics across all embedding values.

    Args:
        vectors (np.ndarray): Shape (N, D)

    Returns:
        dict: mean, std, min, max across all values.
    """
    if vectors.size == 0:
        raise ValueError("vectors array is empty")

    flat = vectors.flatten()

    return {
        "mean": float(np.mean(flat)),
        "std": float(np.std(flat)),
        "min": float(np.min(flat)),
        "max": float(np.max(flat)),
    }


def compute_frequency_ranks(values: np.ndarray) -> np.ndarray:
    """
    Compute frequency ranks for a list of numeric values.

    Example:
        values = [10, 5, 20]
        ranks = [2, 1, 3]

    Args:
        values (np.ndarray): Shape (N,)

    Returns:
        np.ndarray: Shape (N,), containing integer ranks.
    """
    if values.ndim != 1:
        raise ValueError("values must be a 1D numpy array")

    # argsort twice gives rank order
    order = values.argsort()
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(values) + 1)

    return ranks.astype(int)
