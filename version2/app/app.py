"""
app.py

Main Streamlit runtime for version2.

Responsibilities:
- Initialize per-user session ID
- Load precomputed embeddings + stats from Supabase
- Accept resume text or file upload
- Generate resume embedding
- Perform similarity search
- Display job matches, stats panels, and analytics dashboard
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
import json
import numpy as np
import base64

# Add repo root to Python path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
V2_ROOT = os.path.abspath(os.path.join(APP_DIR, ".."))
if V2_ROOT not in sys.path:
    sys.path.insert(0, V2_ROOT)

import streamlit as st

st.set_page_config(
    page_title="Resume Job Tracker",
    page_icon="🔍",
    layout="wide",
)

# -----------------------------------------
# APP TITLE + LOGO
# -----------------------------------------

logo_path = Path(APP_DIR) / "assets" / "Copilot1.png"

with open(logo_path, "rb") as f:
    logo_bytes = f.read()
logo_b64 = base64.b64encode(logo_bytes).decode()

st.markdown(
    f"""
    <div class="app-logo">
        <img src="data:image/png;base64,{logo_b64}" class="logo-img">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center;'>CareerPivots</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Your resume-powered job discovery engine</h4>", unsafe_allow_html=True)

from tracking.session import get_session_id
from core.supabase_client import get_supabase_client
from core.models.embedding_model import load_embedding_provider
from core.utils.text_cleaning import clean_text
from core.similarity import compute_top_k
from services.job_matching import prepare_job_matches, normalize_title
from services.stats_service import load_stats_for_display
from services.prep_service import load_prep_data
from infra.config import load_settings

from app.components.sidebar import render_sidebar
from app.components.job_match_panel import render_job_matches
from app.components.stats_panel import render_stats_panel
from app.components.dashboard_panel import render_dashboard_panel
from app.components.analytics_dashboard import render_analytics_dashboard

from services.resume_extraction_service import extract_experiences, ResumeExtractionError
from services.experience_embedding_service import aggregate_experience_embeddings


def parse_embedding(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    raise TypeError(f"Unexpected embedding type: {type(value)}")


def load_embeddings(supabase):
    """Load job embeddings + metadata from Supabase."""
    response = supabase.table("jobhop_embeddings").select("*").limit(None).execute()
    rows = response.data

    vectors = []
    jobs = []

    for row in rows:
        emb = parse_embedding(row["embedding"])
        arr = np.array(emb, dtype=float)

        # Pool 2D embeddings into a single vector
        if arr.ndim == 2:
            arr = arr.mean(axis=0)

        # Ensure final shape is (384,)
        arr = arr.reshape(-1)

        vectors.append(arr)

        jobs.append({
            "job_id": row.get("job_id"),
            "title": row.get("title"),
            "normalized_title": normalize_title(row.get("title")),
            "description": row.get("description"),
        })

    return vectors, jobs


def inject_css():
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def main():
    # Load config ONCE
    if "config" not in st.session_state:
        st.session_state["config"] = load_settings()

    config = st.session_state["config"]

    inject_css()

    # Per-user session ID
    session_id = get_session_id()

    # Optional tracking dashboard
    show_dashboard = st.sidebar.checkbox("Show Tracking Dashboard")
    if show_dashboard:
        render_dashboard_panel()
        st.stop()

    # Core data load (shared across tabs)
    supabase = get_supabase_client()
    vectors, jobs = load_embeddings(supabase)
    stats_by_title = load_stats_for_display(supabase)

    # Top-level navigation
    main_tab, stats_tab, analytics_tab = st.tabs([
        "Resume Matching",
        "Job Market Statistics",
        "Analytics Dashboard",
    ])

    # -----------------------------------------
    # TAB 1: RESUME MATCHING
    # -----------------------------------------
    with main_tab:
        user_input = render_sidebar(session_id=session_id)
        if "has_run_matching" not in st.session_state:
            st.session_state["has_run_matching"] = False


        if user_input:
            embedding_provider = load_embedding_provider(config)
            cleaned = clean_text(user_input)

            with st.spinner("Parsing your resume into experiences..."):
                try:
                    experiences = extract_experiences(cleaned, config.resume_extraction)
                except ResumeExtractionError as e:
                    st.error(f"Error parsing resume: {e}")
                    st.stop()

            # Store experiences so job_match_panel can access them
            st.session_state["experiences"] = experiences

            with st.spinner("Embedding your experiences..."):
                try:
                    resume_vector = aggregate_experience_embeddings(
                        experiences,
                        embedding_provider,
                    )
                except ValueError as e:
                    st.error(f"Could not embed experiences: {e}")
                    st.stop()

            matches = compute_top_k(resume_vector, vectors, top_k=10)

            with st.expander("See how your resume was parsed"):
                st.json(experiences)

            # ✅ Store results in session_state instead of passing into the panel
            st.session_state["job_match_results"] = prepare_job_matches(
                matches, jobs, stats_by_title
            )
            st.session_state["has_run_matching"] = True

        # ✅ Panel is now read-only: it pulls from session_state
        render_job_matches(num_matches=10)

    # -----------------------------------------
    # TAB 2: JOB MARKET STATISTICS
    # -----------------------------------------
    with stats_tab:
        render_stats_panel(stats_by_title)

    # -----------------------------------------
    # TAB 3: ANALYTICS DASHBOARD
    # -----------------------------------------
    with analytics_tab:
        if "prep" not in st.session_state:
            st.session_state["prep"] = load_prep_data()

        prep = st.session_state["prep"]
        render_analytics_dashboard(prep)


if __name__ == "__main__":
    main()
