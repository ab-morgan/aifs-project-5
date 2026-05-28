"""
test_match_explanation.py

Tests for services/match_explanation_service.py

All HTTP calls to Groq are replaced with fake responses — no API key needed.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock, call

from services.match_explanation_service import (
    explain_match,
    MatchExplanationError,
    MatchExplanationRateLimitError,
    build_explanation_prompt,
)


def _cfg():
    cfg = MagicMock()
    cfg.model = "llama-3.1-8b-instant"
    cfg.endpoint = "https://api.groq.com/openai/v1/chat/completions"
    return cfg


def _job():
    return {"title": "Policy Analyst", "description": "Analyzes federal policy data."}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_explain_match_returns_string(fake_groq_explanation, sample_experiences):
    with patch("services.match_explanation_service.requests.post",
               return_value=fake_groq_explanation):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            result = explain_match(sample_experiences, _job(), _cfg())
    assert isinstance(result, str)
    assert len(result) > 0


def test_explain_match_returns_explanation_text(fake_groq_explanation, sample_experiences):
    with patch("services.match_explanation_service.requests.post",
               return_value=fake_groq_explanation):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            result = explain_match(sample_experiences, _job(), _cfg())
    assert "federal policy" in result.lower() or "policy" in result.lower()


# ---------------------------------------------------------------------------
# Missing API key
# ---------------------------------------------------------------------------

def test_explain_raises_without_api_key(sample_experiences):
    import os
    env = {k: v for k, v in os.environ.items() if k != "GROQ_API_KEY"}
    with patch.dict("os.environ", env, clear=True):
        with pytest.raises(MatchExplanationError, match="GROQ_API_KEY is not set"):
            explain_match(sample_experiences, _job(), _cfg())


# ---------------------------------------------------------------------------
# Rate limiting and retry logic
# ---------------------------------------------------------------------------

def test_explain_retries_on_429_then_succeeds(fake_groq_rate_limit,
                                               fake_groq_explanation,
                                               sample_experiences):
    """Should retry after a 429 and succeed on the next attempt."""
    with patch("services.match_explanation_service.requests.post",
               side_effect=[fake_groq_rate_limit, fake_groq_explanation]):
        with patch("services.match_explanation_service.time.sleep"):
            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
                result = explain_match(sample_experiences, _job(), _cfg())
    assert isinstance(result, str)


def test_explain_raises_rate_limit_after_all_retries(fake_groq_rate_limit, sample_experiences):
    """Should raise MatchExplanationRateLimitError after exhausting all retries."""
    with patch("services.match_explanation_service.requests.post",
               return_value=fake_groq_rate_limit):
        with patch("services.match_explanation_service.time.sleep"):
            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
                with pytest.raises(MatchExplanationRateLimitError):
                    explain_match(sample_experiences, _job(), _cfg())


def test_explain_sleeps_between_retries(fake_groq_rate_limit,
                                         fake_groq_explanation,
                                         sample_experiences):
    """Should call time.sleep between retry attempts."""
    with patch("services.match_explanation_service.requests.post",
               side_effect=[fake_groq_rate_limit, fake_groq_explanation]):
        with patch("services.match_explanation_service.time.sleep") as mock_sleep:
            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
                explain_match(sample_experiences, _job(), _cfg())
    mock_sleep.assert_called_once()


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_explain_raises_on_server_error(fake_groq_error, sample_experiences):
    with patch("services.match_explanation_service.requests.post",
               return_value=fake_groq_error):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            with pytest.raises(MatchExplanationError):
                explain_match(sample_experiences, _job(), _cfg())


def test_explain_error_message_does_not_leak_api_body(fake_groq_error, sample_experiences):
    """The error shown to callers must not contain the raw API response body."""
    with patch("services.match_explanation_service.requests.post",
               return_value=fake_groq_error):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            with pytest.raises(MatchExplanationError) as exc_info:
                explain_match(sample_experiences, _job(), _cfg())
    assert "internal_server_error" not in str(exc_info.value)


def test_explain_raises_on_invalid_json_response(sample_experiences):
    bad_resp = MagicMock()
    bad_resp.status_code = 200
    bad_resp.json.return_value = {
        "choices": [{"message": {"content": "not json"}}]
    }
    with patch("services.match_explanation_service.requests.post", return_value=bad_resp):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            with pytest.raises(MatchExplanationError, match="Invalid JSON"):
                explain_match(sample_experiences, _job(), _cfg())


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def test_build_explanation_prompt_includes_job_description(sample_experiences):
    job = {"description": "Unique job description text XYZ"}
    prompt = build_explanation_prompt(sample_experiences, job)
    assert "Unique job description text XYZ" in prompt


def test_build_explanation_prompt_includes_experience_title(sample_experiences):
    prompt = build_explanation_prompt(sample_experiences, {})
    assert "Policy Analyst" in prompt
