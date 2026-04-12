"""
test_onet_service.py

Tests for services/onet_service.py

All HTTP calls to the O*NET API are replaced with fake responses.
No API key or internet connection needed.
"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from services.onet_service import (
    fetch_questions,
    fetch_results,
    OnetServiceError,
    _headers,
)


# ---------------------------------------------------------------------------
# _headers — key validation
# ---------------------------------------------------------------------------

def test_headers_raises_when_key_missing():
    import os
    env = {k: v for k, v in os.environ.items() if k != "ONET_API_KEY"}
    with patch.dict("os.environ", env, clear=True):
        with pytest.raises(OnetServiceError, match="ONET_API_KEY is not set"):
            _headers()


def test_headers_raises_on_placeholder():
    with patch.dict("os.environ", {"ONET_API_KEY": "PLACEHOLDER_REPLACE_WITH_YOUR_ONET_KEY"}):
        with pytest.raises(OnetServiceError, match="ONET_API_KEY is not set"):
            _headers()


def test_headers_returns_correct_key():
    with patch.dict("os.environ", {"ONET_API_KEY": "real-key-abc"}):
        h = _headers()
    assert h["X-API-Key"] == "real-key-abc"
    assert h["Accept"] == "application/json"


# ---------------------------------------------------------------------------
# fetch_questions — happy path
# ---------------------------------------------------------------------------

def test_fetch_questions_returns_list(fake_onet_questions):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_questions):
            result = fetch_questions()
    assert isinstance(result, list)


def test_fetch_questions_returns_30_items(fake_onet_questions):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_questions):
            result = fetch_questions()
    assert len(result) == 30


def test_fetch_questions_sorted_by_index(fake_onet_questions):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_questions):
            result = fetch_questions()
    indices = [q["index"] for q in result]
    assert indices == sorted(indices)


def test_fetch_questions_has_required_fields(fake_onet_questions):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_questions):
            result = fetch_questions()
    for q in result:
        assert "index" in q
        assert "area" in q
        assert "text" in q


# ---------------------------------------------------------------------------
# fetch_questions — error handling
# ---------------------------------------------------------------------------

def test_fetch_questions_raises_on_api_error(fake_onet_error):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_error):
            with pytest.raises(OnetServiceError, match="O\\*NET questions error"):
                fetch_questions()


# ---------------------------------------------------------------------------
# fetch_results — happy path
# ---------------------------------------------------------------------------

VALID_ANSWERS = "3" * 30   # 30 characters, all valid digits


def test_fetch_results_returns_list(fake_onet_results):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_results):
            result = fetch_results(VALID_ANSWERS)
    assert isinstance(result, list)


def test_fetch_results_returns_six_riasec_dimensions(fake_onet_results):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_results):
            result = fetch_results(VALID_ANSWERS)
    assert len(result) == 6


def test_fetch_results_has_required_fields(fake_onet_results):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_results):
            result = fetch_results(VALID_ANSWERS)
    for r in result:
        assert "code" in r
        assert "title" in r
        assert "score" in r


def test_fetch_results_scores_are_numeric(fake_onet_results):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_results):
            result = fetch_results(VALID_ANSWERS)
    for r in result:
        assert isinstance(r["score"], (int, float))


# ---------------------------------------------------------------------------
# fetch_results — input validation
# ---------------------------------------------------------------------------

def test_fetch_results_raises_on_wrong_length():
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with pytest.raises(OnetServiceError, match="30-character string"):
            fetch_results("333")   # too short


def test_fetch_results_raises_on_non_digits():
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with pytest.raises(OnetServiceError, match="30-character string"):
            fetch_results("a" * 30)   # not digits


def test_fetch_results_raises_on_api_error(fake_onet_error):
    with patch.dict("os.environ", {"ONET_API_KEY": "test-key"}):
        with patch("services.onet_service.requests.get", return_value=fake_onet_error):
            with pytest.raises(OnetServiceError, match="O\\*NET results error"):
                fetch_results(VALID_ANSWERS)
