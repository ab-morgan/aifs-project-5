"""
prep_service.py

Loads precomputed job data (embeddings + stats) from Supabase and caches it
at two levels:

  1. Process-level cache (core/cache.py) — survives across Streamlit sessions
     on the same server process. Data is fetched once and reused until the
     process restarts or the cache is explicitly cleared.

  2. Streamlit session cache (@st.cache_data) — fallback for the analytics
     dashboard which needs the full prep object per session.

The process-level cache means that when 10 users open the app simultaneously,
Supabase is only queried once for the static job data, not 10 times.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any, List, Tuple

import streamlit as st

from core.supabase_client import get_supabase_client
from core.cache import get_cache, set_cache
from core.utils.logging import get_logger

logger = get_logger(__name__)

PAGE_SIZE = 1000
_EMBEDDINGS_CACHE_KEY = "prep:embeddings"
_STATS_CACHE_KEY      = "prep:stats"
_PREP_CACHE_KEY       = "prep:full"


# ─────────────────────────────────────────────────────────────────────────────
# Paginated fetcher
# ─────────────────────────────────────────────────────────────────────────────

def fetch_all_rows(table_name: str) -> List[dict]:
    """Paginated fetch for any Supabase table or view."""
    supabase = get_supabase_client()
    all_rows = []
    page = 0
    while True:
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE - 1
        resp = supabase.table(table_name).select("*").range(start, end).execute()
        rows = resp.data or []
        all_rows.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        page += 1
    return all_rows


# ─────────────────────────────────────────────────────────────────────────────
# Embeddings loader — process-level cache
# ─────────────────────────────────────────────────────────────────────────────

def load_embeddings_cached() -> Tuple[List[np.ndarray], List[dict]]:
    """
    Load job embeddings from Supabase, using a process-level cache.

    Returns:
        (vectors, jobs) where vectors is a list of numpy arrays and
        jobs is a list of metadata dicts {job_id, title, normalized_title, description}.
    """
    cached = get_cache(_EMBEDDINGS_CACHE_KEY)
    if cached is not None:
        logger.info("Embeddings served from process cache.")
        return cached

    logger.info("Loading embeddings from Supabase...")
    rows = fetch_all_rows("jobhop_embeddings")

    from services.job_matching import normalize_title

    vectors: List[np.ndarray] = []
    jobs: List[dict] = []

    for row in rows:
        try:
            emb = row["embedding"]
            if isinstance(emb, str):
                import json
                emb = json.loads(emb)
            arr = np.array(emb, dtype=float)
            if arr.ndim == 2:
                arr = arr.mean(axis=0)
            arr = arr.reshape(-1)
        except Exception as e:
            logger.error("Skipping malformed embedding row job_id=%s: %s", row.get("job_id"), e)
            continue

        vectors.append(arr)
        title = row.get("title") or ""
        jobs.append({
            "job_id":           row.get("job_id"),
            "title":            title,
            "normalized_title": normalize_title(title),
            "description":      row.get("description"),
        })

    logger.info("Loaded %d embeddings.", len(vectors))
    result = (vectors, jobs)
    set_cache(_EMBEDDINGS_CACHE_KEY, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Stats loader — process-level cache
# ─────────────────────────────────────────────────────────────────────────────

def load_stats_cached() -> Dict[str, Any]:
    """
    Load job stats from Supabase, using a process-level cache.

    Returns:
        Dict keyed by normalized job title → stats dict.
    """
    cached = get_cache(_STATS_CACHE_KEY)
    if cached is not None:
        logger.info("Stats served from process cache.")
        return cached

    logger.info("Loading stats from Supabase...")
    from services.stats_service import load_stats_for_display
    supabase = get_supabase_client()
    stats = load_stats_for_display(supabase)
    logger.info("Loaded stats for %d job titles.", len(stats))
    set_cache(_STATS_CACHE_KEY, stats)
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Full prep object — used by analytics dashboard
# ─────────────────────────────────────────────────────────────────────────────

def build_transition_graph(stats_rows: List[dict]) -> Tuple[Dict[str, list], Dict[str, list]]:
    forward: Dict[str, list] = {}
    reverse: Dict[str, list] = {}
    for row in stats_rows:
        job = row.get("job_title", "")
        transitions = row.get("top_transitions") or []
        forward[job] = []
        for t in transitions:
            nxt = t.get("next_job_title")
            count = t.get("count", 0)
            if nxt:
                forward[job].append((nxt, count))
                reverse.setdefault(nxt, []).append((job, count))
    return forward, reverse


@st.cache_data(show_spinner=False)
def load_prep_data() -> Dict[str, Any]:
    """
    Load the full prep object for the analytics dashboard.
    Cached per Streamlit session (re-fetches on new session if process cache
    is also cold, otherwise the inner calls hit the process cache).
    """
    cached = get_cache(_PREP_CACHE_KEY)
    if cached is not None:
        return cached

    stats_rows = fetch_all_rows("jobhop_stats_mv")
    stats_by_title = {row["job_title"]: row for row in stats_rows}

    embedding_rows = fetch_all_rows("jobhop_embeddings")
    embeddings_by_title = {
        (row.get("title") or ""): row["embedding"]
        for row in embedding_rows
        if row.get("title")
    }

    forward_graph, reverse_graph = build_transition_graph(stats_rows)

    industries = sorted({
        row.get("industry")
        for row in stats_rows
        if row.get("industry") not in (None, "", "N/A")
    })

    prep = {
        "stats":               stats_by_title,
        "embeddings":          embeddings_by_title,
        "transitions_forward": forward_graph,
        "transitions_reverse": reverse_graph,
        "all_titles":          list(stats_by_title.keys()),
        "industries":          industries,
    }

    set_cache(_PREP_CACHE_KEY, prep)
    return prep


def clear_prep_cache():
    """Call this after running the prep pipeline to force a fresh load."""
    from core.cache import _GLOBAL_CACHE
    for key in [_EMBEDDINGS_CACHE_KEY, _STATS_CACHE_KEY, _PREP_CACHE_KEY]:
        _GLOBAL_CACHE.pop(key, None)
    logger.info("Prep cache cleared.")
