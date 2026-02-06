"""
app.py

Main Streamlit runtime for version2.

Responsibilities:
- Initialize per-user session ID
- Load precomputed embeddings + stats from Supabase
- Accept resume text or file upload
- Generate resume embedding
- Perform similarity search
- Display job matches and stats panels
"""

from __future__ import annotations

import streamlit as st

from tracking.session import get_session_id
from core.supabase_client import get_supabase_client
from core.models.embedding_model import load_embedding_provider
from core.utils.text_cleaning import clean_text
from core.similarity import compute_top_k
from services.job_matching import prepare_job_matches
from services.stats_service import load_stats_for_display
from app.components.sidebar import render_sidebar
from app.components.job_match_panel import render_job_matches
from app.components.stats_panel import render_stats_panel
from app.components.dashboard_panel import render_dashboard_panel
from pathlib import Path


def load_embeddings(supabase):
    """Load precomputed job embeddings from Supabase."""
    response = supabase.table("job_embeddings").select("*").execute()
    return response.data


def load_jobs(supabase):
    """Load job metadata."""
    response = supabase.table("jobs").select("*").execute()
    return response.data


def inject_css():
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def main():

    st.set_page_config(page_title="Resume Matcher", layout="wide")
    inject_css()

    # Per-user session ID
    session_id = get_session_id()


    show_dashboard = st.sidebar.checkbox("Show Tracking Dashboard")
    if show_dashboard:
        render_dashboard_panel()
        st.stop()
  

    # Sidebar
    user_input = render_sidebar(session_id=session_id)

    # Load data
    supabase = get_supabase_client()
    jobs = load_jobs(supabase)
    embeddings = load_embeddings(supabase)
    stats = load_stats_for_display(supabase)

    # Display stats panel
    render_stats_panel(stats)

    # If user provided resume text or file
    if user_input:
        provider = load_embedding_provider(st.session_state["config"])
        cleaned = clean_text(user_input)
        resume_vector = provider.embed(cleaned)

        # Compute similarity
        matches = compute_top_k(
            resume_vector,
            embeddings,
            top_k=10,
        )

        # Prepare display rows
        display_rows = prepare_job_matches(matches, jobs)

        # Render results
        render_job_matches(display_rows)


if __name__ == "__main__":
    main()
