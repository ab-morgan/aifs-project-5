"""
test_prep_pipeline.py

Tests for the prep pipeline (prep_runner, compute_embeddings, compute_stats,
verify_data) and the runtime cache layer (prep_service).

All Supabase calls are mocked — no database or API keys needed.

Workflow under test:
  make prep  →  verify_data → compute_embeddings → compute_stats
  make dev   →  app loads from Supabase into process cache on first request,
                serves all subsequent users from cache
"""

from __future__ import annotations

import numpy as np
import pytest
from unittest.mock import patch, MagicMock, call

from prep.verify_data import verify_data, _has_rows, _validate_model_config
from prep.compute_embeddings import compute_embeddings
from prep.compute_stats import compute_stats
from prep.prep_runner import run_prep
from services.prep_service import (
    load_embeddings_cached,
    load_stats_cached,
    clear_prep_cache,
    build_transition_graph,
)
from core.cache import clear_cache


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _supabase_with_rows(rows):
    """Mock Supabase client that returns `rows` from any paginated query."""
    client = MagicMock()
    table = MagicMock()
    select = MagicMock()
    range_mock = MagicMock()
    client.table.return_value = table
    table.select.return_value = select
    select.range.return_value = range_mock
    p1 = MagicMock(); p1.data = rows
    p2 = MagicMock(); p2.data = []
    range_mock.execute.side_effect = [p1, p2]
    return client


def _supabase_empty():
    return _supabase_with_rows([])


def _mock_config():
    cfg = MagicMock()
    cfg.embeddings.provider = "sentence_transformer"
    cfg.embeddings.model_name = "all-MiniLM-L6-v2"
    cfg.embeddings.batch_size = 8
    cfg.embeddings.normalize = True
    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# verify_data
# ─────────────────────────────────────────────────────────────────────────────

def test_verify_data_tables_ok_when_all_tables_respond():
    client = MagicMock()
    client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = []
    with patch("prep.verify_data.get_supabase_client", return_value=client):
        with patch("prep.verify_data.load_settings", return_value=_mock_config()):
            report = verify_data()
    assert report["tables_ok"] is True


def test_verify_data_missing_embeddings_when_table_empty():
    client = MagicMock()
    client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = []
    with patch("prep.verify_data.get_supabase_client", return_value=client):
        with patch("prep.verify_data.load_settings", return_value=_mock_config()):
            report = verify_data()
    assert report["missing_embeddings"] is True


def test_verify_data_not_missing_when_rows_exist():
    client = MagicMock()
    client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = [
        {"id": 1}
    ]
    with patch("prep.verify_data.get_supabase_client", return_value=client):
        with patch("prep.verify_data.load_settings", return_value=_mock_config()):
            report = verify_data()
    assert report["missing_embeddings"] is False
    assert report["missing_stats"] is False


def test_verify_data_connection_failure_returns_failed_report():
    client = MagicMock()
    client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("timeout")
    with patch("prep.verify_data.get_supabase_client", return_value=client):
        with patch("prep.verify_data.load_settings", return_value=_mock_config()):
            report = verify_data()
    assert report["tables_ok"] is False


def test_validate_model_config_valid():
    cfg = _mock_config()
    key, ready, details = _validate_model_config(cfg)
    assert ready is True
    assert "sentence_transformer" in key


def test_validate_model_config_missing_provider():
    cfg = MagicMock()
    cfg.embeddings.provider = ""
    cfg.embeddings.model_name = "all-MiniLM-L6-v2"
    key, ready, _ = _validate_model_config(cfg)
    assert ready is False


# ─────────────────────────────────────────────────────────────────────────────
# compute_embeddings
# ─────────────────────────────────────────────────────────────────────────────

_RAW_JOBS = [
    {"id": 1, "title": "Policy Analyst", "description": "Analyzes policy.", "industry": "Gov"},
    {"id": 2, "title": "Data Analyst",   "description": "Analyzes data.",   "industry": "Tech"},
]


def test_compute_embeddings_processes_all_jobs():
    client = _supabase_with_rows(_RAW_JOBS)
    # existing IDs query returns empty (nothing embedded yet)
    existing_resp = MagicMock(); existing_resp.data = []
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=_RAW_JOBS), MagicMock(data=[]),   # raw jobs pages
        MagicMock(data=[]),                               # existing IDs page
    ]

    mock_provider = MagicMock()
    mock_provider.embed.return_value = np.array([[0.1, 0.2, 0.3]])

    with patch("prep.compute_embeddings.get_supabase_client", return_value=client):
        with patch("prep.compute_embeddings.load_settings", return_value=_mock_config()):
            with patch("prep.compute_embeddings.load_embedding_provider", return_value=mock_provider):
                result = compute_embeddings()

    assert result["status"] == "success"
    assert result["processed"] == 2


def test_compute_embeddings_skips_existing():
    client = MagicMock()
    # raw jobs: 2 rows
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=_RAW_JOBS), MagicMock(data=[]),
        MagicMock(data=[{"job_id": 1}, {"job_id": 2}]), MagicMock(data=[]),  # both exist
    ]

    mock_provider = MagicMock()
    mock_provider.embed.return_value = np.array([[0.1, 0.2, 0.3]])

    with patch("prep.compute_embeddings.get_supabase_client", return_value=client):
        with patch("prep.compute_embeddings.load_settings", return_value=_mock_config()):
            with patch("prep.compute_embeddings.load_embedding_provider", return_value=mock_provider):
                result = compute_embeddings(force=False)

    assert result["skipped"] == 2
    assert result["processed"] == 0


def test_compute_embeddings_no_jobs_returns_early():
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=[]),  # empty raw jobs
    ]
    with patch("prep.compute_embeddings.get_supabase_client", return_value=client):
        with patch("prep.compute_embeddings.load_settings", return_value=_mock_config()):
            with patch("prep.compute_embeddings.load_embedding_provider"):
                result = compute_embeddings()
    assert result["status"] == "no_jobs"


# ─────────────────────────────────────────────────────────────────────────────
# compute_stats
# ─────────────────────────────────────────────────────────────────────────────

_RAW_WITH_TRANSITIONS = [
    {"id": 1, "title": "Policy Analyst", "industry": "Gov",
     "tenure_days": 730, "growth_rate": 0.05, "next_job_title": "Senior Policy Analyst"},
    {"id": 2, "title": "Policy Analyst", "industry": "Gov",
     "tenure_days": 912, "growth_rate": 0.05, "next_job_title": "Program Manager"},
    {"id": 3, "title": "Data Analyst",   "industry": "Tech",
     "tenure_days": 365, "growth_rate": 0.12, "next_job_title": "Data Scientist"},
]


def test_compute_stats_produces_correct_titles():
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=_RAW_WITH_TRANSITIONS), MagicMock(data=[]),
    ]
    upsert_mock = MagicMock()
    client.table.return_value.upsert.return_value.execute = upsert_mock

    with patch("prep.compute_stats.get_supabase_client", return_value=client):
        result = compute_stats()

    assert result["status"] == "success"
    assert result["titles_processed"] == 2   # Policy Analyst + Data Analyst


def test_compute_stats_frequency_rank_most_common_is_1():
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=_RAW_WITH_TRANSITIONS), MagicMock(data=[]),
    ]
    captured = []
    def capture_upsert(rows, **kwargs):
        captured.extend(rows)
        return MagicMock()
    client.table.return_value.upsert.side_effect = capture_upsert

    with patch("prep.compute_stats.get_supabase_client", return_value=client):
        compute_stats()

    policy = next(r for r in captured if r["job_title"] == "Policy Analyst")
    assert policy["frequency_rank"] == 1   # 2 occurrences vs 1 for Data Analyst


def test_compute_stats_empty_data_returns_early():
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=[]),
    ]
    with patch("prep.compute_stats.get_supabase_client", return_value=client):
        result = compute_stats()
    assert result["status"] == "no_data"


# ─────────────────────────────────────────────────────────────────────────────
# prep_runner orchestration
# ─────────────────────────────────────────────────────────────────────────────

def test_run_prep_skips_embeddings_when_present():
    report = {
        "tables_ok": True, "model_ready": True,
        "missing_embeddings": False, "missing_stats": False,
    }
    with patch("prep.prep_runner.verify_data", return_value=report):
        with patch("prep.prep_runner.compute_embeddings") as mock_emb:
            with patch("prep.prep_runner.compute_stats") as mock_stats:
                result = run_prep(force=False)

    mock_emb.assert_not_called()
    mock_stats.assert_not_called()
    assert result["status"] == "success"


def test_run_prep_runs_embeddings_when_missing():
    report = {
        "tables_ok": True, "model_ready": True,
        "missing_embeddings": True, "missing_stats": True,
    }
    with patch("prep.prep_runner.verify_data", return_value=report):
        with patch("prep.prep_runner.compute_embeddings", return_value={"status": "success", "processed": 10}) as mock_emb:
            with patch("prep.prep_runner.compute_stats", return_value={"status": "success", "titles_processed": 5}):
                result = run_prep(force=False)

    mock_emb.assert_called_once_with(force=False)
    assert result["embeddings_generated"] is True


def test_run_prep_force_reruns_everything():
    report = {
        "tables_ok": True, "model_ready": True,
        "missing_embeddings": False, "missing_stats": False,
    }
    with patch("prep.prep_runner.verify_data", return_value=report):
        with patch("prep.prep_runner.compute_embeddings", return_value={"status": "success", "processed": 10}) as mock_emb:
            with patch("prep.prep_runner.compute_stats", return_value={"status": "success", "titles_processed": 5}):
                run_prep(force=True)

    mock_emb.assert_called_once_with(force=True)


def test_run_prep_aborts_when_tables_not_ready():
    report = {"tables_ok": False, "model_ready": True,
              "missing_embeddings": True, "missing_stats": True}
    with patch("prep.prep_runner.verify_data", return_value=report):
        with patch("prep.prep_runner.compute_embeddings") as mock_emb:
            result = run_prep()
    mock_emb.assert_not_called()
    assert result["status"] == "failed"


# ─────────────────────────────────────────────────────────────────────────────
# prep_service — process-level cache
# ─────────────────────────────────────────────────────────────────────────────

_EMBEDDING_ROWS = [
    {"job_id": 1, "title": "Policy Analyst", "description": "Analyzes policy.",
     "embedding": [0.1, 0.2, 0.3]},
    {"job_id": 2, "title": "Data Analyst",   "description": "Analyzes data.",
     "embedding": [0.4, 0.5, 0.6]},
]

_STATS_ROWS = [
    {"job_title": "Policy Analyst", "count": 100, "percent": 0.05,
     "frequency_rank": 3, "avg_tenure_days": 730, "median_tenure_days": 700,
     "top_transitions": [], "industry": "Gov", "growth_rate": 0.05},
]


@pytest.fixture(autouse=True)
def reset_process_cache():
    """Clear the process-level cache before each test."""
    clear_cache()
    yield
    clear_cache()


def test_load_embeddings_cached_returns_vectors_and_jobs():
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=_EMBEDDING_ROWS), MagicMock(data=[]),
    ]
    with patch("services.prep_service.get_supabase_client", return_value=client):
        vectors, jobs = load_embeddings_cached()

    assert len(vectors) == 2
    assert len(jobs) == 2
    assert isinstance(vectors[0], np.ndarray)
    assert jobs[0]["title"] == "Policy Analyst"


def test_load_embeddings_cached_hits_supabase_only_once():
    """Second call must be served from cache, not Supabase."""
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=_EMBEDDING_ROWS), MagicMock(data=[]),
    ]
    with patch("services.prep_service.get_supabase_client", return_value=client):
        load_embeddings_cached()
        load_embeddings_cached()   # second call

    # Supabase was only called for the first load (2 pages = 2 execute calls)
    assert client.table.return_value.select.return_value.range.return_value.execute.call_count == 2


def test_load_embeddings_cached_empty_when_prep_not_run():
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=[]),
    ]
    with patch("services.prep_service.get_supabase_client", return_value=client):
        vectors, jobs = load_embeddings_cached()
    assert vectors == []
    assert jobs == []


def test_clear_prep_cache_forces_fresh_load():
    client = MagicMock()
    client.table.return_value.select.return_value.range.return_value.execute.side_effect = [
        MagicMock(data=_EMBEDDING_ROWS), MagicMock(data=[]),
        MagicMock(data=_EMBEDDING_ROWS), MagicMock(data=[]),  # second load after clear
    ]
    with patch("services.prep_service.get_supabase_client", return_value=client):
        load_embeddings_cached()
        clear_prep_cache()
        load_embeddings_cached()

    assert client.table.return_value.select.return_value.range.return_value.execute.call_count == 4


def test_build_transition_graph_forward():
    rows = [
        {"job_title": "Analyst", "top_transitions": [
            {"next_job_title": "Senior Analyst", "count": 50},
            {"next_job_title": "Manager",         "count": 30},
        ]},
    ]
    forward, reverse = build_transition_graph(rows)
    assert ("Senior Analyst", 50) in forward["Analyst"]
    assert ("Analyst", 50) in reverse["Senior Analyst"]


def test_build_transition_graph_empty():
    forward, reverse = build_transition_graph([])
    assert forward == {}
    assert reverse == {}
