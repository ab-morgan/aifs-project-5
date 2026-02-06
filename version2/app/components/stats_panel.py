"""
stats_panel.py

Displays global stats computed during the PREP phase.
"""

from __future__ import annotations

import streamlit as st


def render_stats_panel(stats):
    st.sidebar.title("Dataset Stats")

    if not stats:
        st.sidebar.warning("Stats not available.")
        return

    st.sidebar.markdown(f"**Mean:** {stats['mean']:.4f}")
    st.sidebar.markdown(f"**Std Dev:** {stats['std']:.4f}")
    st.sidebar.markdown(f"**Min:** {stats['min']:.4f}")
    st.sidebar.markdown(f"**Max:** {stats['max']:.4f}")
