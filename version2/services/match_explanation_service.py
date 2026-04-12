from __future__ import annotations
import os
import json
import time
import requests
from typing import Dict, Any, List
from infra.config import ResumeExtractionConfig
from core.utils.logging import get_logger

_log = get_logger(__name__)

_MAX_RETRIES = 4
_RETRY_DELAY = 1.0  # seconds; Groq rate limit resets within 1s


class MatchExplanationError(Exception):
    pass

class MatchExplanationRateLimitError(MatchExplanationError):
    pass


def build_explanation_prompt(experiences, job):
    return f"""
You are an expert career coach.

Explain why the candidate's experience matches the job below.
Be concise, specific, and reference the candidate's real experience.

Return ONLY valid JSON:

{{
  "explanation": "A short explanation of why the candidate matches this job."
}}

Candidate experiences:
{json.dumps(experiences, indent=2)}

Job description:
\"\"\"{job.get("description", "")}\"\"\"
""".strip()


def explain_match(
    experiences: List[Dict[str, Any]],
    job: Dict[str, Any],
    cfg: ResumeExtractionConfig,
    api_key: str | None = None,
) -> str:

    api_key = api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MatchExplanationError("GROQ_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prompt = build_explanation_prompt(experiences, job)

    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": "You output only strict JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    resp = None
    for attempt in range(_MAX_RETRIES):
        resp = requests.post(cfg.endpoint, headers=headers, json=payload, timeout=60)
        if resp.status_code != 429:
            break
        time.sleep(_RETRY_DELAY)
    if resp.status_code == 429:
        raise MatchExplanationRateLimitError("Rate limit exceeded after retries")
    if resp.status_code != 200:
        # Log the detail internally but don't expose raw API response to callers
        _log.error("Groq API error %s: %s", resp.status_code, resp.text[:500])
        raise MatchExplanationError(
            f"Groq API returned status {resp.status_code}. Check logs for details."
        )

    content = resp.json()["choices"][0]["message"]["content"]

    try:
        data = json.loads(content)
        return data["explanation"]
    except Exception as e:
        raise MatchExplanationError(f"Invalid JSON from Groq: {e}\n{content[:500]}")
