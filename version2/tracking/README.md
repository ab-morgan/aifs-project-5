Tracking Module

The tracking module provides a lightweight event‑logging system for the Streamlit application. It enables per‑session analytics, user‑behavior insights, and debugging visibility without adding complexity to the core app logic. This layer is intentionally simple, append‑only, and designed to integrate cleanly with Supabase.

Directory Structure

tracking/
init.py
session.py
event_logger.py
supabase_logger.py

File Overview

session.py
Generates and stores a stable per‑user session ID using Streamlit’s session_state.

event_logger.py
Creates structured event objects and forwards them to the Supabase writer.

supabase_logger.py
Writes events to the events table in Supabase using the shared client.

Event Schema

Events follow the structure defined in version2/schemas/event.py:
session_id — unique identifier for the user session
event_type — string describing the event
timestamp — UTC timestamp
payload — JSON metadata

Supabase Table Definition

create table if not exists events (
id bigint generated always as identity primary key,
session_id text not null,
event_type text not null,
timestamp timestamptz not null default now(),
payload jsonb
);

create index if not exists idx_events_session_id on events (session_id);
create index if not exists idx_events_event_type on events (event_type);
create index if not exists idx_events_timestamp on events (timestamp desc);

Logging Events

Example usage:

from tracking.event_logger import log_event
from tracking.session  import get_session_id

session_id = get_session_id()

log_event(
session_id=session_id,
event_type="resume_uploaded",
payload={"filename": "resume.pdf"}
)

Use Cases

Tracking resume uploads
Monitoring job‑match clicks
Measuring engagement with dashboard panels
Debugging user flows
Building analytics dashboards

Design Principles

Append‑only
Schema‑light (JSON payloads)
Low overhead
Modular
Supabase‑native

Future Extensions

Aggregated analytics
Materialized views
Admin dashboards
Event replay
Funnel analysis