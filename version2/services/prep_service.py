"""
prep_service.py

Loads all job data, embeddings, and transitions from Supabase
using pagination, normalizes them, and returns a unified prep object
for use across the application (matching engine, Sankey diagrams, etc.).
"""


from __future__ import annotations
from typing import Dict, Any, List, Tuple
from core.supabase_client import get_supabase_client
import streamlit as st


PAGE_SIZE = 1000


# ---------------------------------------------------------
# PAGINATED FETCHER
# ---------------------------------------------------------
def fetch_all_rows(table_name: str) -> List[dict]:
    """
    Generic paginated fetcher for any Supabase table or view.
    Ensures we bypass the 1000-row PostgREST limit.
    """
    supabase = get_supabase_client()

    all_rows = []
    page = 0

    while True:
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE - 1

        response = (
            supabase
            .table(table_name)
            .select("*")
            .range(start, end)
            .execute()
        )

        rows = response.data or []
        all_rows.extend(rows)

        if len(rows) < PAGE_SIZE:
            break

        page += 1

    return all_rows


# ---------------------------------------------------------
# TRANSITION GRAPH BUILDER
# ---------------------------------------------------------
def build_transition_graph(stats_rows: List[dict]) -> Tuple[Dict[str, list], Dict[str, list]]:
    """
    Builds:
      - forward transitions: job → [(next_job, count)]
      - reverse transitions: job → [(prev_job, count)]
    """
    forward = {}
    reverse = {}

    for row in stats_rows:
        job = row["job_title"]
        transitions = row.get("top_transitions") or []

        forward[job] = []

        for t in transitions:
            nxt = t.get("next_job_title")
            count = t.get("count", 0)

            if nxt:
                forward[job].append((nxt, count))

                # Build reverse mapping
                if nxt not in reverse:
                    reverse[nxt] = []
                reverse[nxt].append((job, count))

    return forward, reverse


# ---------------------------------------------------------
# MAIN PREP LOADER
# ---------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_prep_data() -> Dict[str, Any]:
    """
    Loads all job titles, stats, embeddings, and transitions.
    Cached so it runs only once per session.
    """

    # 1. Load stats
    stats_rows = fetch_all_rows("jobhop_stats_mv")

    stats_by_title = {row["job_title"]: row for row in stats_rows}

    # 2. Load embeddings
    embedding_rows = fetch_all_rows("jobhop_embeddings")
    embeddings_by_title = {
        (row.get("job_title") or row.get("title")): row["embedding"]
        for row in embedding_rows
        if (row.get("job_title") or row.get("title"))
    }

    # 3. Build forward + reverse transition graphs
    forward_graph, reverse_graph = build_transition_graph(stats_rows)

    # ⭐ NEW: Extract industries
    industries = sorted({
        row.get("industry")
        for row in stats_rows
        if row.get("industry") not in (None, "", "N/A")
    })

    # 4. Unified prep object
    prep = {
        "stats": stats_by_title,
        "embeddings": embeddings_by_title,
        "transitions_forward": forward_graph,
        "transitions_reverse": reverse_graph,
        "all_titles": list(stats_by_title.keys()),
        "industries": industries,
    }

    return prep


