"""
stats_service.py

Loads precomputed stats from Supabase and prepares them for display
in the Streamlit sidebar.

This keeps the UI clean and avoids direct Supabase calls in app.py.
"""

from __future__ import annotations

from typing import Dict, Any
from core.supabase_client import get_supabase_client


def load_stats_for_display(supabase=None) -> Dict[str, Any]:
    """
    Load global embedding stats from Supabase.

    Returns:
        dict with keys: mean, std, min, max
    """
    supabase = supabase or get_supabase_client()

    response = supabase.table("job_stats").select("*").limit(1).execute()
    data = getattr(response, "data", None) or response.get("data", [])

    if not data:
        return {}

    row = data[0]

    return {
        "mean": row.get("mean"),
        "std": row.get("std"),
        "min": row.get("min"),
        "max": row.get("max"),
    }
