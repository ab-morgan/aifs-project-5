"""
event_logger.py

Provides a simple interface for logging events inside the app.

Events follow the schema defined in version2/schemas/event.py:
- session_id
- event_type
- timestamp
- payload
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from version2.schemas.event import Event
from version2.tracking.supabase_logger import write_event


def log_event(session_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    """
    Create an Event object and send it to Supabase.

    Args:
        session_id: Unique session identifier
        event_type: Name of the event (e.g., "resume_uploaded")
        payload: Arbitrary metadata
    """
    event = Event(
        session_id=session_id,
        event_type=event_type,
        timestamp=datetime.utcnow(),
        payload=payload,
    )

    write_event(event)
