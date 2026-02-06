"""
job_family_clustering.py

Provides utilities to cluster jobs into "job families" based on their
embeddings. This is intended for analytics and future UI features
(e.g., browsing by family, coverage analysis).

Current implementation:
- KMeans clustering on job embeddings
- Returns a mapping: job_id -> cluster_label
"""

from __future__ import annotations

from typing import Dict, List, Any

import numpy as np
from sklearn.cluster import KMeans


def cluster_job_families(
    embeddings: List[Dict[str, Any]],
    n_clusters: int = 10,
    random_state: int = 42,
) -> Dict[int, int]:
    """
    Cluster jobs into families using KMeans on embeddings.

    Args:
        embeddings: List of dicts with keys {job_id, embedding}
        n_clusters: Number of clusters (job families)
        random_state: Random seed for reproducibility

    Returns:
        dict: {job_id: cluster_label}
    """
    if not embeddings:
        return {}

    job_ids = [row["job_id"] for row in embeddings]
    vectors = np.array([row["embedding"] for row in embeddings], dtype=float)

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
    labels = model.fit_predict(vectors)

    return {job_id: int(label) for job_id, label in zip(job_ids, labels)}
