"""
compute_stats.py

Computes aggregate statistics for job embeddings and uploads them to Supabase.
This includes:
- vector norms
- embedding distribution statistics
- frequency ranks
- any additional stats needed by the UI

This script is part of the PREP pipeline and should NOT run during the
Streamlit runtime. It is designed to be idempotent and safe to re-run.
"""

from __future__ import annotations

import logging
import numpy as np
from typing import Dict, Any, List

from infra.config import load_config
from core.supabase_client import get_supabase_client
from core.stats import (
    compute_vector_norms,
    compute_embedding_distribution,
    compute_frequency_ranks,
)

logger = logging.getLogger(__name__)


def _fetch_embeddings(supabase) -> List[Dict[str, Any]]:
    """
    Fetch embeddings from Supabase.

    Returns:
        List of dicts with keys: job_id, embedding
    """
    try:
        response = supabase.table("job_embeddings").select("*").execute()
        data = getattr(response, "data", None) or response.get("data", [])
        logger.info(f"Fetched {len(data)} embeddings.")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch embeddings: {e}")
        raise


def _upload_stats(supabase, rows: List[Dict[str, Any]]):
    """
    Upload computed stats to Supabase.
    """
    try:
        supabase.table("job_stats").insert(rows).execute()
    except Exception as e:
        logger.error(f"Failed to upload stats batch: {e}")
        raise


def compute_stats() -> Dict[str, Any]:
    """
    Main entrypoint for computing statistics.

    Returns:
        dict: Summary of the stats computation process.
    """
    logger.info("Starting compute_stats step...")

    config = load_config()
    supabase = get_supabase_client()

    # Fetch embeddings
    embeddings = _fetch_embeddings(supabase)
    if not embeddings:
        logger.warning("No embeddings found. Cannot compute stats.")
        return {"status": "no_embeddings"}

    # Convert embeddings to numpy arrays
    vectors = np.array([e["embedding"] for e in embeddings])
    job_ids = [e["job_id"] for e in embeddings]

    # Compute vector norms
    norms = compute_vector_norms(vectors)

    # Compute distribution statistics
    dist_stats = compute_embedding_distribution(vectors)

    # Compute frequency ranks (simple example: rank by vector norm)
    freq_ranks = compute_frequency_ranks(norms)

    # Prepare rows for upload
    rows_to_upload = []
    for job_id, norm, rank in zip(job_ids, norms, freq_ranks):
        rows_to_upload.append(
            {
                "job_id": job_id,
                "vector_norm": float(norm),
                "frequency_rank": int(rank),
                "mean": float(dist_stats["mean"]),
                "std": float(dist_stats["std"]),
                "min": float(dist_stats["min"]),
                "max": float(dist_stats["max"]),
            }
        )

    # Upload stats
    _upload_stats(supabase, rows_to_upload)

    summary = {
        "status": "success",
        "total_embeddings": len(embeddings),
        "stats_uploaded": len(rows_to_upload),
    }

    logger.info(f"compute_stats summary: {summary}")
    return summary


if __name__ == "__main__":
    logging.basicConfig(
        filename="logs/prep.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = compute_stats()
    print(result)
