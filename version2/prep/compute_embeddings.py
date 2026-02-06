"""
compute_embeddings.py

Generates embeddings for all job descriptions using the embedding provider
configured in infra/settings.toml. Uploads results to Supabase and optionally
caches them locally.

This script is part of the PREP pipeline and should NOT run during the
Streamlit runtime. It is designed to be idempotent and safe to re-run.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any

from infra.config import load_config
from core.supabase_client import get_supabase_client
from core.utils.text_cleaning import clean_text
from core.models.embedding_model import load_embedding_provider
from core.embeddings import normalize_vector

logger = logging.getLogger(__name__)


def _fetch_raw_jobs(supabase) -> List[Dict[str, Any]]:
    """
    Fetch raw job descriptions from Supabase.

    Returns:
        List of dicts with keys: id, title, description, etc.
    """
    try:
        response = supabase.table("jobs").select("*").execute()
        data = getattr(response, "data", None) or response.get("data", [])
        logger.info(f"Fetched {len(data)} raw job records.")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch raw jobs: {e}")
        raise


def _batch(iterable, batch_size: int):
    """Yield items in batches."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


def _upload_embeddings(supabase, rows: List[Dict[str, Any]]):
    """
    Upload a batch of embeddings to Supabase.
    """
    try:
        supabase.table("job_embeddings").insert(rows).execute()
    except Exception as e:
        logger.error(f"Failed to upload embeddings batch: {e}")
        raise


def compute_embeddings() -> Dict[str, Any]:
    """
    Main entrypoint for generating embeddings.

    Returns:
        dict: Summary of the embedding generation process.
    """
    logger.info("Starting compute_embeddings step...")

    config = load_config()
    supabase = get_supabase_client()

    embeddings_cfg = config.get("embeddings", {})
    batch_size = embeddings_cfg.get("batch_size", 16)
    normalize = embeddings_cfg.get("normalize", True)

    # Load embedding provider (OpenAI, Ollama, etc.)
    provider = load_embedding_provider(config)
    logger.info(f"Using embedding provider: {provider}")

    # Fetch raw job data
    jobs = _fetch_raw_jobs(supabase)
    if not jobs:
        logger.warning("No jobs found. Nothing to embed.")
        return {"status": "no_jobs"}

    total = len(jobs)
    processed = 0
    failed = 0

    for batch in _batch(jobs, batch_size):
        rows_to_upload = []

        for job in batch:
            job_id = job.get("id")
            text = job.get("description", "")

            try:
                cleaned = clean_text(text)
                vector = provider.embed(cleaned)

                if normalize:
                    vector = normalize_vector(vector)

                rows_to_upload.append(
                    {
                        "job_id": job_id,
                        "embedding": vector,
                    }
                )
                processed += 1

            except Exception as e:
                logger.error(f"Embedding failed for job_id={job_id}: {e}")
                failed += 1

        if rows_to_upload:
            _upload_embeddings(supabase, rows_to_upload)
            logger.info(f"Uploaded batch of {len(rows_to_upload)} embeddings.")

    summary = {
        "status": "success",
        "total_jobs": total,
        "processed": processed,
        "failed": failed,
        "provider": str(provider),
    }

    logger.info(f"compute_embeddings summary: {summary}")
    return summary


if __name__ == "__main__":
    logging.basicConfig(
        filename="logs/prep.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = compute_embeddings()
    print(result)
