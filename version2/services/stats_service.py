"""
stats_service.py

Loads precomputed stats from Supabase and prepares them for display
in the Streamlit sidebar.
"""

from __future__ import annotations

from typing import Dict, Any
from core.supabase_client import get_supabase_client
import json


def load_stats_for_display(supabase):
    """
    Load and normalize job statistics from Supabase using manual pagination.
    Converts tenure from days → years, keeps percent as a fraction,
    and returns a dict keyed by job_title.
    """

    all_rows = []
    page = 0
    page_size = 1000

    # -----------------------------
    # PAGINATION LOOP (correct)
    # -----------------------------
    while True:
        start = page * page_size
        end = start + page_size - 1

        response = (
            supabase
            .table("jobhop_stats_mv")   # <-- your MV with 2955 rows
            .select("*")
            .range(start, end)
            .execute()
        )

        rows = response.data or []
        all_rows.extend(rows)

        if len(rows) < page_size:
            break

        page += 1

    # -----------------------------
    # NORMALIZATION (corrected)
    # -----------------------------
    normalized = {}

    for row in all_rows:   # <-- FIXED: iterate over ALL rows
        avg_days = row.get("avg_tenure_days")
        median_days = row.get("median_tenure_days")

        avg_years = (avg_days / 365) if isinstance(avg_days, (int, float)) else None
        median_years = (median_days / 365) if isinstance(median_days, (int, float)) else None

        normalized[row["job_title"]] = {
            "Job Title": row["job_title"],
            "Count": row.get("count"),
            "Percent of Database": row.get("percent"),
            "Frequency Rank": row.get("frequency_rank"),
            "Avg Tenure (Years)": avg_years,
            "Median Tenure (Years)": median_years,
            "Top Transitions": row.get("top_transitions"),
            "Industry": row.get("industry"),
            "Growth Rate": row.get("growth_rate"),
        }

    return normalized


def get_stats_for_job(title: str, stats_by_title: dict):
    """
    Version2-compatible lookup helper.
    """

    if not title:
        return None

    if title in stats_by_title:
        return stats_by_title[title]

    lower_title = title.lower()
    for key in stats_by_title.keys():
        if key.lower() == lower_title:
            return stats_by_title[key]

    return None
