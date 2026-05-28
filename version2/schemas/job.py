"""
job.py

Schema for job metadata loaded from Supabase.
Used by:
- job_matching service
- runtime UI
- analytics
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
