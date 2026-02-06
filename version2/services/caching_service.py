"""
caching_service.py

Provides optional caching utilities for runtime performance.

This is intentionally lightweight for now, but can be expanded to:
- Cache embeddings locally
- Cache job metadata
- Cache stats
- Cache model instances

Streamlit's built-in caching decorators are used here.
"""

from __future__ import annotations

import streamlit as st
from core.supabase_client import get_supabase_client


@st.cache_data(show_spinner=False)
def cached_jobs():
    """Cache job metadata."""
    supabase = get_supabase_client()
    response = supabase.table("jobs").select("*").execute()
    return response.data


@st.cache_data(show_spinner=False)
def cached_embeddings():
    """Cache job embeddings."""
    supabase = get_supabase_client()
    response = supabase.table("job_embeddings").select("*").execute()
    return response.data


@st.cache_data(show_spinner=False)
def cached_stats():
    """Cache global stats."""
    supabase = get_supabase_client()
    response = supabase.table("job_stats").select("*").limit(1).execute()
    data = getattr(response, "data", None) or response.get("data", [])
    return data[0] if data else {}
