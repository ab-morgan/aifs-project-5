"""
job_matching.py

Responsible for transforming raw similarity results into clean,
UI‑ready job match rows.

This service:
- Joins similarity results with job metadata
- Sorts by similarity
- Formats fields for display
"""

from __future__ import annotations

from typing import List, Dict, Any


def prepare_job_matches(matches: List[Dict[str, Any]], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Combine similarity results with job metadata.

    Args:
        matches: List of dicts with keys {job_id, similarity}
        jobs: List of job metadata dicts

    Returns:
        List of dicts ready for UI display.
    """
    job_lookup = {job["id"]: job for job in jobs}

    rows = []
    for m in matches:
        job_id = m["job_id"]
        similarity = m["similarity"]

        job = job_lookup.get(job_id)
        if not job:
            continue

        rows.append(
            {
                "job_id": job_id,
                "title": job.get("title", "Untitled Role"),
                "company": job.get("company", "Unknown"),
                "location": job.get("location", "Unknown"),
                "similarity": similarity,
            }
        )

    # Sort descending by similarity
    rows.sort(key=lambda r: r["similarity"], reverse=True)
    return rows
