"""
analytics_dashboard.py

A polished wrapper for all analytics tools:
- Sankey Diagram
- Multi-Level Sankey
- Transition Explorer

This module provides a single function:
    render_analytics_dashboard(prep)

which can be called from app.py inside main().
"""

import streamlit as st

from components.sankey_panel import (
    render_sankey_panel,
    render_multilevel_sankey
)

from components.transition_explorer import (
    render_transition_explorer
)


def render_analytics_dashboard(prep):
    """
    Renders the full analytics dashboard with tabs.
    """

    st.markdown("## 📊 Career Flow Analytics Dashboard")
    st.markdown("""
    Explore how people move between jobs across the entire dataset.
    Use the tabs below to visualize:
    - **Career transition flows** (Sankey)
    - **Multi-step pathways** (Multi-Level Sankey)
    - **Filtered transition patterns** (Transition Explorer)
    """)

    tab1, tab2, tab3 = st.tabs([
        "Sankey Diagram",
        "Multi‑Level Sankey",
        "Transition Explorer"
    ])

    with tab1:
        st.markdown("### 🔀 Single‑Step Career Flow")
        st.markdown("Visualize where people go *from* or *to* a selected job.")
        render_sankey_panel(prep)

    with tab2:
        st.markdown("### 🔁 Multi‑Level Career Pathways")
        st.markdown("See two‑step flows: Job → Next Job → Next Job.")
        render_multilevel_sankey(prep)

    with tab3:
        st.markdown("### 🔎 Transition Explorer")
        st.markdown("Filter transitions by count, industry, or growth rate.")
        render_transition_explorer(prep)
