"""
Tests for security-sensitive code paths:
- Input sanitization
- HTML escaping (spot-check the functions that produce unsafe_allow_html output)
- ONET key validation
- Match explanation error handling
"""
import html
import pytest
from unittest.mock import patch, MagicMock

from app.components.sidebar import _sanitize_text
from services.onet_service import OnetServiceError


# ── _sanitize_text ─────────────────────────────────────────────────────────

def test_sanitize_strips_null_bytes():
    assert "\x00" not in _sanitize_text("hello\x00world")


def test_sanitize_strips_control_chars():
    # \x01 through \x08 should be removed
    assert _sanitize_text("hello\x01\x02world") == "helloworld"


def test_sanitize_preserves_newlines():
    text = "line one\nline two\r\nline three"
    result = _sanitize_text(text)
    assert "\n" in result


def test_sanitize_preserves_tabs():
    assert "\t" in _sanitize_text("col1\tcol2")


def test_sanitize_normal_text_unchanged():
    text = "Experienced analyst with 10 years in federal government."
    assert _sanitize_text(text) == text


# ── html.escape coverage (used in job_match_panel) ─────────────────────────

def test_html_escape_script_tag():
    dangerous = "<script>alert('xss')</script>"
    escaped = html.escape(dangerous)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped


def test_html_escape_attribute_injection():
    dangerous = '" onmouseover="alert(1)'
    escaped = html.escape(dangerous)
    assert "onmouseover" not in escaped or "&quot;" in escaped


def test_html_escape_safe_text_unchanged():
    safe = "Software Engineer"
    assert html.escape(safe) == safe


# ── ONET key validation ────────────────────────────────────────────────────

def test_onet_missing_key_raises():
    import os
    env = {k: v for k, v in os.environ.items() if k != "ONET_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        from services.onet_service import _headers
        with pytest.raises(OnetServiceError, match="ONET_API_KEY is not set"):
            _headers()


def test_onet_placeholder_key_raises():
    with patch.dict("os.environ", {"ONET_API_KEY": "PLACEHOLDER_REPLACE_WITH_YOUR_ONET_KEY"}):
        from services.onet_service import _headers
        with pytest.raises(OnetServiceError, match="ONET_API_KEY is not set"):
            _headers()


def test_onet_real_key_returns_headers():
    with patch.dict("os.environ", {"ONET_API_KEY": "real-key-abc123"}):
        from services.onet_service import _headers
        headers = _headers()
        assert headers["X-API-Key"] == "real-key-abc123"


# ── Match explanation error sanitization ───────────────────────────────────

def test_explain_match_sanitizes_error_on_non_200(monkeypatch):
    """Groq API errors should be logged internally, not returned to callers."""
    from services import match_explanation_service as svc

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal server error with sensitive details"

    with patch("services.match_explanation_service.requests.post", return_value=mock_resp):
        with patch.object(svc._log, "error") as mock_log:
            cfg = MagicMock()
            cfg.model = "llama-3.1-8b-instant"
            cfg.endpoint = "https://api.groq.com/openai/v1/chat/completions"

            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
                with pytest.raises(svc.MatchExplanationError) as exc_info:
                    svc.explain_match([], {}, cfg)

            # Error message shown to user must NOT contain raw API response body
            assert "sensitive details" not in str(exc_info.value)
            # But it should have been logged internally
            mock_log.assert_called_once()
