import pytest
from unittest.mock import MagicMock
from services.stats_service import load_stats_for_display, get_stats_for_job


def _make_supabase_with_rows(rows):
    """Build a mock Supabase client that returns `rows` from a paginated query."""
    client = MagicMock()
    table = MagicMock()
    client.table.return_value = table

    # Chain: .select("*").range(start, end).execute()
    select_mock = MagicMock()
    range_mock = MagicMock()
    execute_mock = MagicMock()

    table.select.return_value = select_mock
    select_mock.range.return_value = range_mock

    # First page returns rows, second page returns empty (stops pagination)
    execute_mock.data = rows
    empty_execute = MagicMock()
    empty_execute.data = []
    range_mock.execute.side_effect = [execute_mock, empty_execute]

    return client


def test_load_stats_returns_dict():
    rows = [
        {"job_title": "Data Scientist", "count": 100, "percent": 0.05,
         "frequency_rank": 3, "avg_tenure_days": 730, "median_tenure_days": 700,
         "top_transitions": [], "industry": "Tech", "growth_rate": 0.1},
    ]
    client = _make_supabase_with_rows(rows)
    result = load_stats_for_display(client)
    assert "Data Scientist" in result


def test_load_stats_converts_tenure_to_years():
    rows = [
        {"job_title": "Analyst", "count": 50, "percent": 0.02,
         "frequency_rank": 10, "avg_tenure_days": 365, "median_tenure_days": 730,
         "top_transitions": [], "industry": "Finance", "growth_rate": 0.0},
    ]
    client = _make_supabase_with_rows(rows)
    result = load_stats_for_display(client)
    assert result["Analyst"]["Avg Tenure (Years)"] == pytest.approx(1.0)
    assert result["Analyst"]["Median Tenure (Years)"] == pytest.approx(2.0)


def test_get_stats_for_job_case_insensitive():
    stats = {"data scientist": {"Frequency Rank": 3}}
    assert get_stats_for_job("Data Scientist", stats) == {"Frequency Rank": 3}


def test_get_stats_for_job_missing_returns_none():
    assert get_stats_for_job("Nonexistent Job", {}) is None
