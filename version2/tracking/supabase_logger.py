"""
supabase_logger.py

Writes tracking events to Supabase.

Table schema (recommended):

create table if not exists events (
    id bigint generated always as identity primary key,
    session_id text not null,
    event_type text not null,
    timestamp timestamptz not null,
    payload jsonb
);

This module is intentionally simple and append-only.
"""

from __future__ import annotations

from typing import Any, Dict

from version2.core.supabase_client import get_supabase_client
from version2.schemas.event import Event


def write_event(event: Event) -> None:
    """
    Insert an event into the Supabase 'events' table.
    """
    supabase = get_supabase_client()

    supabase.table("events").insert(
        {
            "session_id": event.session_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "payload": event.payload,
        }
    ).execute()
