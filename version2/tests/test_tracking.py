from tracking.event_logger import log_event
from tracking.session import get_session_id
from unittest.mock import patch


def test_session_id_stable():
    # Simulate Streamlit session_state
    import streamlit as st
    st.session_state.clear()

    sid1 = get_session_id()
    sid2 = get_session_id()
    assert sid1 == sid2


@patch("tracking.supabase_logger.write_event")
def test_log_event(mock_write):
    log_event("abc123", "resume_uploaded", {"file": "resume.pdf"})
    mock_write.assert_called_once()
