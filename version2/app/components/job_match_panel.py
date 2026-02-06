"""
job_match_panel.py

Displays job match results in a clean, readable format.
"""

from __future__ import annotations

import streamlit as st


def render_job_matches(rows):
    st.header("Top Job Matches")

    if not rows:
        st.info("No matches found.")
        return

    for row in rows:
        with st.container():
            st.subheader(row["title"])
            st.markdown(f"**Similarity:** {row['similarity']:.4f}")
            st.markdown(f"**Company:** {row.get('company', 'N/A')}")
            st.markdown(f"**Location:** {row.get('location', 'N/A')}")
            st.markdown("---")
