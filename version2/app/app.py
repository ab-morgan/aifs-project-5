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

import sys
import os

# Add repo root to Python path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
V2_ROOT = os.path.abspath(os.path.join(APP_DIR, ".."))
if V2_ROOT not in sys.path:
    sys.path.insert(0, V2_ROOT)


import streamlit as st

st.set_page_config(
    page_title="Resume Job Tracker",
    page_icon="🔍"
)

from tracking.session import get_session_id
from core.supabase_client import get_supabase_client
from core.models.embedding_model import load_embedding_provider
from core.utils.text_cleaning import clean_text
from core.similarity import compute_top_k
from services.job_matching import prepare_job_matches, normalize_title
from services.stats_service import load_stats_for_display
from app.components.sidebar import render_sidebar
from app.components.job_match_panel import render_job_matches
from app.components.stats_panel import render_stats_panel
from app.components.dashboard_panel import render_dashboard_panel
from pathlib import Path
from infra.config import load_settings


import json
import numpy as np



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

        # ⭐ CRITICAL FIX: pool 2D embeddings into a single vector
        if arr.ndim == 2:
            arr = arr.mean(axis=0)

        # ⭐ Ensure final shape is (384,)
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


    if "config" not in st.session_state:
        st.session_state["config"] = load_settings()

    #st.write("DEBUG AFTER CONFIG:", st.session_state.get("config"))

    config = st.session_state["config"]

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
    #jobs = load_jobs(supabase)
    vectors, jobs = load_embeddings(supabase)

    stats_by_title = load_stats_for_display(supabase)


    # Display stats panel
    render_stats_panel(stats_by_title)

    # If user provided resume text or file
    if user_input:


        # Initialize config if missing
        if "config" not in st.session_state:
            st.session_state["config"] = {
                "provider": "supabase",
                "embedding_model": "text-embedding-3-small",
                "normalize": True,
                "batch_size": 128,
            }



        provider = load_embedding_provider(st.session_state["config"])
        cleaned = clean_text(user_input)
        resume_vector = provider.embed(cleaned)

        # Compute similarity
        matches = compute_top_k(
            resume_vector,
            vectors,
            top_k=10,
        )

        # Prepare display rows
        display_rows = prepare_job_matches(matches, jobs, stats_by_title)

        # Render results
        render_job_matches(display_rows, st.session_state["num_matches"])



if __name__ == "__main__":
    main()
