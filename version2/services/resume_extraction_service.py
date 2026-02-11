# version2/app/services/resume_extraction_service.py
from __future__ import annotations

import os
import json
import requests
from typing import List, Dict, Any

from infra.config import ResumeExtractionConfig


class ResumeExtractionError(Exception):
    pass


def _build_extraction_prompt(resume_text: str) -> str:
    return f"""
You are an expert resume parser.

Extract the candidate's professional experience from the resume below and return a JSON array.
Each item in the array must have this structure:

{{
  "job_title": "string",
  "company": "string or null",
  "location": "string or null",
  "start_date": "YYYY-MM or null",
  "end_date": "YYYY-MM or null",
  "is_current": true/false,
  "bullets": ["bullet 1", "bullet 2", ...],
  "skills": ["skill1", "skill2", ...]
}}

Rules:
- Only include real work/volunteer/internship experiences.
- Normalize dates to "YYYY-MM" when possible; otherwise use null.
- Bullets should be short, action-oriented statements.
- Skills should be a flat list of key skills inferred from that role.
- Do NOT include any explanation, only valid JSON.

Resume:
\"\"\"{resume_text}\"\"\"
""".strip()


def extract_experiences(
    resume_text: str,
    cfg: ResumeExtractionConfig,
    api_key: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Use Groq (via config) to extract structured experiences from a resume.
    """
    api_key = api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ResumeExtractionError("GROQ_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prompt = _build_extraction_prompt(resume_text)

    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": "You output only strict JSON. No prose."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }

    resp = requests.post(cfg.endpoint, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise ResumeExtractionError(
            f"Groq API error {resp.status_code}: {resp.text[:500]}"
        )

    try:
        content = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise ResumeExtractionError(f"Unexpected Groq response format: {e}")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ResumeExtractionError(
            f"Groq returned invalid JSON: {e}\nContent: {content[:500]}"
        )

    if not isinstance(data, list):
        raise ResumeExtractionError(f"Expected a JSON array, got: {type(data)}")

    return data
