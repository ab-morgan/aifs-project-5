"""
dashboard_panel.py

A Streamlit dashboard for visualizing tracking events stored in Supabase.

Features:
- Event count over time
- Event type distribution
- Session activity table
- Raw payload inspection

This panel is optional and can be added to the main UI or placed
behind a sidebar toggle.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from version2.core.supabase_client import get_supabase_client


def _load_events():
    """Fetch all events from Supabase."""
    supabase = get_supabase_client()
    response = supabase.table("events").select("*").order("timestamp", desc=False).execute()
    return response.data or []


def render_dashboard_panel():
    st.header("📊 Tracking Dashboard")

    events = _load_events()
    if not events:
        st.info("No events logged yet.")
        return

    df = pd.DataFrame(events)

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    st.subheader("Event Volume Over Time")
    st.line_chart(df.groupby(df["timestamp"].dt.floor("min")).size())

    st.subheader("Event Types")
    st.bar_chart(df["event_type"].value_counts())

    st.subheader("Session Activity")
    st.dataframe(
        df.groupby("session_id")
        .size()
        .reset_index(name="event_count")
        .sort_values("event_count", ascending=False)
    )

    st.subheader("Raw Events")
    st.dataframe(df)
