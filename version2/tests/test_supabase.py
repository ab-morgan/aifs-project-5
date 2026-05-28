"""
test_supabase.py

Tests for Supabase-dependent code:
- core/supabase_client.py
- services/stats_service.py  (paginated loading)
- app/app.py load_embeddings (malformed row handling)

All Supabase calls are replaced with mock objects — no database needed.
"""

from __future__ import annotations

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from services.stats_service import load_stats_for_display, get_stats_for_job


# ---------------------------------------------------------------------------
# supabase_client — connection setup
# ---------------------------------------------------------------------------

def test_get_supabase_client_raises_without_url():
    import os
    env = {k: v for k, v in os.environ.items()
           if k not in ("SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY")}
    with patch.dict("os.environ", env, clear=True):
        # Clear the lru_cache so it re-evaluates env vars
        from core.supabase_client import get_supabase_client
        get_supabase_client.cache_clear()
        with pytest.raises(ValueError, match="SUPABASE_URL"):
            get_supabase_client()


def test_get_supabase_client_raises_without_key():
    import os
    env = {k: v for k, v in os.environ.items() if k != "SUPABASE_PUBLISHABLE_KEY"}
    env["SUPABASE_URL"] = "https://example.supabase.co"
    with patch.dict("os.environ", env, clear=True):
        from core.supabase_client import get_supabase_client
        get_supabase_client.cache_clear()
        with pytest.raises(ValueError, match="SUPABASE_PUBLISHABLE_KEY"):
            get_supabase_client()


# ---------------------------------------------------------------------------
# load_stats_for_display — happy path
# ---------------------------------------------------------------------------

def test_load_stats_returns_all_rows(mock_supabase_stats):
    result = load_stats_for_display(mock_supabase_stats)
    assert len(result) == 2
    assert "Policy Analyst" in result
    assert "Data Analyst" in result


def test_load_stats_converts_tenure_days_to_years(mock_supabase_stats):
    result = load_stats_for_display(mock_supabase_stats)
    # 912 days / 365 ≈ 2.498 years
    assert result["Policy Analyst"]["Avg Tenure (Years)"] == pytest.approx(912 / 365)


def test_load_stats_median_tenure_converted(mock_supabase_stats):
    result = load_stats_for_display(mock_supabase_stats)
    assert result["Policy Analyst"]["Median Tenure (Years)"] == pytest.approx(730 / 365)


def test_load_stats_preserves_percent(mock_supabase_stats):
    result = load_stats_for_display(mock_supabase_stats)
    assert result["Policy Analyst"]["Percent of Database"] == pytest.approx(0.045)


def test_load_stats_preserves_frequency_rank(mock_supabase_stats):
    result = load_stats_for_display(mock_supabase_stats)
    assert result["Data Analyst"]["Frequency Rank"] == 5


def test_load_stats_preserves_top_transitions(mock_supabase_stats):
    result = load_stats_for_display(mock_supabase_stats)
    transitions = result["Policy Analyst"]["Top Transitions"]
    assert isinstance(transitions, list)
    assert transitions[0]["next_job_title"] == "Senior Policy Analyst"


# ---------------------------------------------------------------------------
# load_stats_for_display — edge cases
# ---------------------------------------------------------------------------

def test_load_stats_handles_null_tenure():
    """Rows with null tenure days should produce None, not crash."""
    rows = [{"job_title": "Analyst", "count": 10, "percent": 0.01,
             "frequency_rank": 50, "avg_tenure_days": None,
             "median_tenure_days": None, "top_transitions": [],
             "industry": "Gov", "growth_rate": 0.0}]
    client = _make_single_page_client(rows)
    result = load_stats_for_display(client)
    assert result["Analyst"]["Avg Tenure (Years)"] is None


def test_load_stats_empty_database():
    """Empty database should return empty dict, not crash."""
    client = _make_single_page_client([])
    result = load_stats_for_display(client)
    assert result == {}


def _make_single_page_client(rows):
    client = MagicMock()
    table = MagicMock()
    select = MagicMock()
    range_mock = MagicMock()
    client.table.return_value = table
    table.select.return_value = select
    select.range.return_value = range_mock
    page1 = MagicMock(); page1.data = rows
    page2 = MagicMock(); page2.data = []
    range_mock.execute.side_effect = [page1, page2]
    return client


# ---------------------------------------------------------------------------
# get_stats_for_job
# ---------------------------------------------------------------------------

def test_get_stats_exact_match(sample_stats_by_title):
    result = get_stats_for_job("policy analyst", sample_stats_by_title)
    assert result is not None
    assert result["Frequency Rank"] == 12


def test_get_stats_case_insensitive(sample_stats_by_title):
    result = get_stats_for_job("POLICY ANALYST", sample_stats_by_title)
    assert result is not None


def test_get_stats_missing_title_returns_none(sample_stats_by_title):
    assert get_stats_for_job("Astronaut", sample_stats_by_title) is None


def test_get_stats_empty_title_returns_none(sample_stats_by_title):
    assert get_stats_for_job("", sample_stats_by_title) is None


# ---------------------------------------------------------------------------
# load_embeddings_cached (prep_service) — malformed row handling
# ---------------------------------------------------------------------------

def test_load_embeddings_cached_skips_malformed_rows():
    """Rows with bad embedding data should be skipped, not crash the load."""
    from core.cache import clear_cache
    from services.prep_service import load_embeddings_cached
    clear_cache()

    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=[
            {"job_id": 1, "title": "Good Job", "description": "desc",
             "embedding": [0.1, 0.2, 0.3]},
            {"job_id": 2, "title": "Bad Job",  "description": "x",
             "embedding": "not-valid-json"},
        ]),
        MagicMock(data=[]),
    ]

    with patch("services.prep_service.get_supabase_client", return_value=client):
        vectors, jobs = load_embeddings_cached()

    assert len(vectors) == 1
    assert jobs[0]["title"] == "Good Job"
    clear_cache()
