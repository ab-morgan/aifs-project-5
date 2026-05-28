"""
session.py

Provides a stable per-user session ID for Streamlit runtime.

Uses Streamlit's session_state to ensure:
- One ID per user session
- No collisions
- No external dependencies
"""

from __future__ import annotations

import uuid
import streamlit as st


def get_session_id() -> str:
    """
    Return a stable session ID for the current Streamlit session.
    """
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]
