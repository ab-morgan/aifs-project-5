"""
event.py

Schema for tracking events (future use).
This will support:
- session tracking
- user interactions
- analytics
- Supabase logging

The tracking layer will write these events.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass
class Event:
    session_id: str
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]
