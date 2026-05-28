"""
compute_embeddings.py

Generates embeddings for all job descriptions in jobhop_raw and upserts
them into jobhop_embeddings.

- Idempotent: uses upsert on job_id so re-running is safe
- Paginated: fetches raw jobs in pages to handle large datasets
- Skips jobs that already have embeddings (unless --force is passed)
"""

from __future__ import annotations

import numpy as np
import logging
from typing import List, Dict, Any

from infra.config import load_settings
from core.supabase_client import get_supabase_client
from core.utils.text_cleaning import clean_text
from core.utils.logging import get_logger
from core.models.embedding_model import load_embedding_provider
from core.embeddings import normalize_vector

logger = get_logger(__name__)

PAGE_SIZE = 1000


def _fetch_raw_jobs(supabase) -> List[Dict[str, Any]]:
    """Paginated fetch of all rows from jobhop_raw."""
    all_rows = []
    page = 0
    while True:
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE - 1
        resp = supabase.table("jobhop_raw").select("*").range(start, end).execute()
        rows = resp.data or []
        all_rows.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        page += 1
    logger.info("Fetched %d raw job records.", len(all_rows))
    return all_rows


def _fetch_existing_job_ids(supabase) -> set:
    """Return the set of job_ids that already have embeddings."""
    existing = set()
    page = 0
    while True:
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE - 1
        resp = supabase.table("jobhop_embeddings").select("job_id").range(start, end).execute()
        rows = resp.data or []
        for r in rows:
            existing.add(r["job_id"])
        if len(rows) < PAGE_SIZE:
            break
        page += 1
    return existing


def _upsert_embeddings(supabase, rows: List[Dict[str, Any]]):
    """Upsert a batch of embeddings (safe to re-run)."""
    supabase.table("jobhop_embeddings").upsert(rows, on_conflict="job_id").execute()


def _batch(items, size):
    for i in range(0, len(items), size):
        yield items[i: i + size]


def compute_embeddings(force: bool = False) -> Dict[str, Any]:
    """
    Generate and store embeddings for all jobs in jobhop_raw.

    Args:
        force: If True, recompute embeddings even for jobs that already have them.

    Returns:
        Summary dict with counts of processed / skipped / failed jobs.
    """
    logger.info("Starting compute_embeddings (force=%s)...", force)

    config = load_settings()
    supabase = get_supabase_client()

    provider = load_embedding_provider(config)
    batch_size = config.embeddings.batch_size
    should_normalize = config.embeddings.normalize

    jobs = _fetch_raw_jobs(supabase)
    if not jobs:
        logger.warning("No jobs found in jobhop_raw. Nothing to embed.")
        return {"status": "no_jobs", "processed": 0, "skipped": 0, "failed": 0}

    existing_ids = set() if force else _fetch_existing_job_ids(supabase)
    logger.info("%d jobs already have embeddings.", len(existing_ids))

    to_process = [j for j in jobs if j["id"] not in existing_ids]
    skipped = len(jobs) - len(to_process)
    logger.info("%d jobs to embed, %d skipped.", len(to_process), skipped)

    processed = 0
    failed = 0

    for batch in _batch(to_process, batch_size):
        rows_to_upsert = []
        for job in batch:
            job_id = job.get("id")
            text = job.get("description") or job.get("title") or ""
            try:
                cleaned = clean_text(text)
                vector = provider.embed([cleaned])

                arr = np.array(vector)
                if arr.ndim == 2:
                    arr = arr[0]
                if should_normalize:
                    arr = np.array(normalize_vector(arr.tolist()))

                rows_to_upsert.append({
                    "job_id": job_id,
                    "title": job.get("title"),
                    "description": job.get("description"),
                    "embedding": arr.tolist(),
                })
                processed += 1
            except Exception as e:
                logger.error("Embedding failed for job_id=%s: %s", job_id, e)
                failed += 1

        if rows_to_upsert:
            try:
                _upsert_embeddings(supabase, rows_to_upsert)
                logger.info("Upserted batch of %d embeddings.", len(rows_to_upsert))
            except Exception as e:
                logger.error("Batch upsert failed: %s", e)
                failed += len(rows_to_upsert)
                processed -= len(rows_to_upsert)

    summary = {
        "status": "success",
        "total_jobs": len(jobs),
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "provider": str(provider),
    }
    logger.info("compute_embeddings summary: %s", summary)
    return summary
