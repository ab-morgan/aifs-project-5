"""
compute_stats.py

Computes per-job-title statistics from jobhop_raw and upserts them into
jobhop_stats. The app reads jobhop_stats_mv (a view over jobhop_stats) at
runtime.

Statistics computed per job title:
- count                 — number of occurrences in the dataset
- percent               — fraction of total rows
- frequency_rank        — rank by count (1 = most common)
- avg_tenure_days       — average tenure in days (if tenure data exists)
- median_tenure_days    — median tenure in days
- top_transitions       — top 5 next jobs people moved to, with counts/percents
- industry              — most common industry for this title
- growth_rate           — placeholder (0.0) unless source data provides it

Idempotent: uses upsert on job_title.
"""

from __future__ import annotations

import logging
import statistics
from collections import Counter, defaultdict
from typing import Dict, Any, List

from infra.config import load_settings
from core.supabase_client import get_supabase_client
from core.utils.logging import get_logger

logger = get_logger(__name__)

PAGE_SIZE = 1000


def _fetch_all_raw(supabase) -> List[Dict[str, Any]]:
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
    logger.info("Fetched %d raw rows for stats computation.", len(all_rows))
    return all_rows


def _upsert_stats(supabase, rows: List[Dict[str, Any]]):
    supabase.table("jobhop_stats").upsert(rows, on_conflict="job_title").execute()


def compute_stats() -> Dict[str, Any]:
    """
    Compute per-title statistics from jobhop_raw and upsert into jobhop_stats.

    Returns:
        Summary dict.
    """
    logger.info("Starting compute_stats...")

    supabase = get_supabase_client()
    rows = _fetch_all_raw(supabase)

    if not rows:
        logger.warning("No rows in jobhop_raw. Cannot compute stats.")
        return {"status": "no_data", "titles_processed": 0}

    total = len(rows)

    # ── Group rows by job title ───────────────────────────────────────────
    by_title: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        title = (row.get("title") or "").strip()
        if title:
            by_title[title].append(row)

    # ── Frequency rank (most common = rank 1) ─────────────────────────────
    title_counts = {t: len(v) for t, v in by_title.items()}
    sorted_titles = sorted(title_counts, key=lambda t: title_counts[t], reverse=True)
    freq_rank = {t: i + 1 for i, t in enumerate(sorted_titles)}

    # ── Build stats rows ──────────────────────────────────────────────────
    stats_rows = []
    for title, job_rows in by_title.items():
        count = len(job_rows)
        percent = count / total if total > 0 else 0.0

        # Tenure (days) — use tenure_days column if present, else None
        tenure_values = [
            r["tenure_days"] for r in job_rows
            if r.get("tenure_days") is not None and isinstance(r["tenure_days"], (int, float))
        ]
        avg_tenure = statistics.mean(tenure_values) if tenure_values else None
        med_tenure = statistics.median(tenure_values) if tenure_values else None

        # Industry — most common value for this title
        industries = [r.get("industry") for r in job_rows if r.get("industry")]
        industry = Counter(industries).most_common(1)[0][0] if industries else None

        # Growth rate — use growth_rate column if present
        growth_values = [
            r["growth_rate"] for r in job_rows
            if r.get("growth_rate") is not None and isinstance(r["growth_rate"], (int, float))
        ]
        growth_rate = statistics.mean(growth_values) if growth_values else 0.0

        # Top transitions — use next_job_title column if present
        next_titles = [
            r.get("next_job_title") for r in job_rows if r.get("next_job_title")
        ]
        transition_counts = Counter(next_titles)
        top_transitions = [
            {
                "next_job_title": nxt,
                "count": cnt,
                "percent": cnt / count,
            }
            for nxt, cnt in transition_counts.most_common(5)
        ]

        stats_rows.append({
            "job_title":          title,
            "count":              count,
            "percent":            percent,
            "frequency_rank":     freq_rank[title],
            "avg_tenure_days":    avg_tenure,
            "median_tenure_days": med_tenure,
            "top_transitions":    top_transitions,
            "industry":           industry,
            "growth_rate":        growth_rate,
        })

    # ── Upsert in batches ─────────────────────────────────────────────────
    BATCH = 500
    for i in range(0, len(stats_rows), BATCH):
        batch = stats_rows[i: i + BATCH]
        try:
            _upsert_stats(supabase, batch)
            logger.info("Upserted stats batch %d–%d.", i, i + len(batch))
        except Exception as e:
            logger.error("Stats upsert failed for batch %d: %s", i, e)

    summary = {
        "status": "success",
        "total_raw_rows": total,
        "titles_processed": len(stats_rows),
    }
    logger.info("compute_stats summary: %s", summary)
    return summary
