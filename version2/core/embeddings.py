"""
embeddings.py

Utility functions for working with embedding vectors.

Includes:
- normalize_vector
- ensure_vector
- ensure_matrix
"""

from __future__ import annotations

import numpy as np
from typing import List


def normalize_vector(vec: List[float]) -> List[float]:
    """
    Normalize a vector to unit length.

    Args:
        vec: List of floats.

    Returns:
        List[float]: Normalized vector.
    """
    arr = np.array(vec, dtype=float)
    norm = np.linalg.norm(arr)

    if norm == 0:
        return arr.tolist()

    return (arr / norm).tolist()


def ensure_vector(vec) -> np.ndarray:
    """
    Ensure input is a 1D numpy array.
    """
    arr = np.array(vec, dtype=float)
    if arr.ndim != 1:
        raise ValueError("Expected a 1D vector")
    return arr


def ensure_matrix(mat) -> np.ndarray:
    """
    Ensure input is a 2D numpy array.
    """
    arr = np.array(mat, dtype=float)
    if arr.ndim != 2:
        raise ValueError("Expected a 2D matrix")
    return arr
