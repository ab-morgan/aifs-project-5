"""
onet_service.py

Wraps the O*NET Web Services API for the Interest Profiler (Mini-IP).

Endpoints used:
  GET /mnm/interestprofiler/questions_30  — fetch all 30 questions
  GET /mnm/interestprofiler/results       — submit answers, get RIASEC scores

Auth: X-API-Key header (set ONET_API_KEY in .env)
Base URL: https://api-v2.onetcenter.org
"""

from __future__ import annotations
import os
import requests
from typing import Any

_BASE = "https://api-v2.onetcenter.org"


class OnetServiceError(Exception):
    pass


def _headers() -> dict[str, str]:
    key = os.getenv("ONET_API_KEY", "PLACEHOLDER_ONET_API_KEY")
    return {"X-API-Key": key, "Accept": "application/json"}


def fetch_questions() -> list[dict[str, Any]]:
    """
    Fetch all 30 Mini-IP questions in a single request.
    Returns a list of {index, area, text} dicts sorted by index.
    """
    url = f"{_BASE}/mnm/interestprofiler/questions_30"
    resp = requests.get(url, headers=_headers(), params={"start": 1, "end": 30}, timeout=15)
    if resp.status_code != 200:
        raise OnetServiceError(f"O*NET questions error {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    questions = data.get("question", [])
    return sorted(questions, key=lambda q: q["index"])


def fetch_results(answers: str) -> list[dict[str, Any]]:
    """
    Submit a 30-character answer string (digits 1-5) and get RIASEC scores.
    Returns a list of {code, title, score, description} dicts.
    """
    if len(answers) != 30 or not answers.isdigit():
        raise OnetServiceError("answers must be a 30-character string of digits 1-5")
    url = f"{_BASE}/mnm/interestprofiler/results"
    resp = requests.get(url, headers=_headers(), params={"answers": answers}, timeout=15)
    if resp.status_code != 200:
        raise OnetServiceError(f"O*NET results error {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    return data.get("result", [])
