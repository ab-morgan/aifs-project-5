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
from services.stats_service import get_stats_for_job

def normalize_title(title: str) -> str:
    return title.strip().lower()


def prepare_job_matches(matches, jobs, stats_by_title):
    display_rows = []

    for job_index, similarity in matches:
        job = jobs[job_index]

        title = job.get("title")
        description = job.get("description", "No description available.")
        normalized = job.get("normalized_title")

        raw_stats = stats_by_title.get(normalized, {})

        row = {
            "title": title,
            "description": description,
            "similarity": float(similarity) * 100,

            "stats": {
                "percent_of_db": raw_stats.get("Percent of Database"),
                "frequency_rank": raw_stats.get("Frequency Rank"),
                "avg_tenure_years": raw_stats.get("Avg Tenure (Years)"),
                "median_tenure_years": raw_stats.get("Median Tenure (Years)"),
                "top_transitions": raw_stats.get("Top Transitions"),
                "industry": raw_stats.get("Industry"),
                "growth_rate": raw_stats.get("Growth Rate"),
            },

        }


        display_rows.append(row)

    return display_rows
