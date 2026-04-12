"""
test_resume_extraction.py

Tests for services/resume_extraction_service.py

All HTTP calls to Groq are replaced with fake responses — no API key needed.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock

from services.resume_extraction_service import extract_experiences, ResumeExtractionError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cfg():
    cfg = MagicMock()
    cfg.model = "llama-3.1-8b-instant"
    cfg.endpoint = "https://api.groq.com/openai/v1/chat/completions"
    return cfg


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_extract_experiences_returns_list(fake_groq_extraction, sample_resume_text):
    with patch("services.resume_extraction_service.requests.post",
               return_value=fake_groq_extraction):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            result = extract_experiences(sample_resume_text, _cfg())
    assert isinstance(result, list)
    assert len(result) == 1


def test_extract_experiences_has_expected_fields(fake_groq_extraction, sample_resume_text):
    with patch("services.resume_extraction_service.requests.post",
               return_value=fake_groq_extraction):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            result = extract_experiences(sample_resume_text, _cfg())
    exp = result[0]
    assert "job_title" in exp
    assert "bullets" in exp
    assert "skills" in exp


def test_extract_experiences_correct_job_title(fake_groq_extraction, sample_resume_text):
    with patch("services.resume_extraction_service.requests.post",
               return_value=fake_groq_extraction):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            result = extract_experiences(sample_resume_text, _cfg())
    assert result[0]["job_title"] == "Policy Analyst"


# ---------------------------------------------------------------------------
# Missing API key
# ---------------------------------------------------------------------------

def test_extract_raises_without_api_key(sample_resume_text):
    import os
    env = {k: v for k, v in os.environ.items() if k != "GROQ_API_KEY"}
    with patch.dict("os.environ", env, clear=True):
        with pytest.raises(ResumeExtractionError, match="GROQ_API_KEY is not set"):
            extract_experiences(sample_resume_text, _cfg())


# ---------------------------------------------------------------------------
# API error responses
# ---------------------------------------------------------------------------

def test_extract_raises_on_api_error(fake_groq_error, sample_resume_text):
    with patch("services.resume_extraction_service.requests.post",
               return_value=fake_groq_error):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            with pytest.raises(ResumeExtractionError):
                extract_experiences(sample_resume_text, _cfg())


def test_extract_raises_on_invalid_json(sample_resume_text):
    """Groq returns something that isn't valid JSON."""
    bad_resp = MagicMock()
    bad_resp.status_code = 200
    bad_resp.json.return_value = {
        "choices": [{"message": {"content": "This is not JSON at all."}}]
    }
    with patch("services.resume_extraction_service.requests.post", return_value=bad_resp):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            with pytest.raises(ResumeExtractionError, match="invalid JSON"):
                extract_experiences(sample_resume_text, _cfg())


def test_extract_raises_when_response_is_not_list(sample_resume_text):
    """Groq returns a JSON object instead of an array."""
    bad_resp = MagicMock()
    bad_resp.status_code = 200
    bad_resp.json.return_value = {
        "choices": [{"message": {"content": json.dumps({"job_title": "Analyst"})}}]
    }
    with patch("services.resume_extraction_service.requests.post", return_value=bad_resp):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            with pytest.raises(ResumeExtractionError, match="Expected a JSON array"):
                extract_experiences(sample_resume_text, _cfg())
