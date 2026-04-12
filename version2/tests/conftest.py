"""
conftest.py

Shared pytest fixtures for the CareerPivots test suite.

All external services (Groq, O*NET, Supabase) are replaced with fakes
so tests run instantly, offline, and without API keys.
"""

from __future__ import annotations

import json
import pytest
import numpy as np
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Fake API response builder
# ---------------------------------------------------------------------------

def _fake_response(status: int, body) -> MagicMock:
    """Build a fake requests.Response object."""
    resp = MagicMock()
    resp.status_code = status
    resp.text = json.dumps(body) if not isinstance(body, str) else body
    resp.json.return_value = body
    return resp


# ---------------------------------------------------------------------------
# Config fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def groq_cfg():
    """Minimal ResumeExtractionConfig pointing at Groq."""
    cfg = MagicMock()
    cfg.model = "llama-3.1-8b-instant"
    cfg.endpoint = "https://api.groq.com/openai/v1/chat/completions"
    return cfg


# ---------------------------------------------------------------------------
# Groq API fake responses
# ---------------------------------------------------------------------------

SAMPLE_EXPERIENCES = [
    {
        "job_title": "Policy Analyst",
        "company": "Department of Labor",
        "location": "Washington, DC",
        "start_date": "2018-06",
        "end_date": "2024-01",
        "is_current": False,
        "bullets": [
            "Analyzed federal workforce data to inform policy decisions",
            "Produced quarterly reports for senior leadership",
        ],
        "skills": ["data analysis", "policy writing", "Excel"],
    }
]

SAMPLE_EXPLANATION = "Your federal policy experience aligns well with this role."


@pytest.fixture
def fake_groq_extraction():
    """Fake a successful Groq resume extraction response."""
    body = {
        "choices": [
            {"message": {"content": json.dumps(SAMPLE_EXPERIENCES)}}
        ]
    }
    return _fake_response(200, body)


@pytest.fixture
def fake_groq_explanation():
    """Fake a successful Groq match explanation response."""
    body = {
        "choices": [
            {"message": {"content": json.dumps({"explanation": SAMPLE_EXPLANATION})}}
        ]
    }
    return _fake_response(200, body)


@pytest.fixture
def fake_groq_rate_limit():
    """Fake a Groq 429 rate-limit response."""
    return _fake_response(429, {"error": "rate_limit_exceeded"})


@pytest.fixture
def fake_groq_error():
    """Fake a Groq 500 server error response."""
    return _fake_response(500, {"error": "internal_server_error"})


# ---------------------------------------------------------------------------
# O*NET API fake responses
# ---------------------------------------------------------------------------

SAMPLE_QUESTIONS = [
    {"index": i, "area": area, "text": f"Sample question {i}"}
    for i, area in enumerate(
        ["realistic", "investigative", "artistic", "social", "enterprising", "conventional"] * 5,
        start=1,
    )
]

SAMPLE_RIASEC_RESULTS = [
    {"code": "realistic",     "title": "Realistic",     "score": 20, "description": "Hands-on work."},
    {"code": "investigative", "title": "Investigative", "score": 35, "description": "Research and analysis."},
    {"code": "artistic",      "title": "Artistic",      "score": 15, "description": "Creative work."},
    {"code": "social",        "title": "Social",        "score": 28, "description": "Helping others."},
    {"code": "enterprising",  "title": "Enterprising",  "score": 22, "description": "Leading and persuading."},
    {"code": "conventional",  "title": "Conventional",  "score": 18, "description": "Organized, detail work."},
]


@pytest.fixture
def fake_onet_questions():
    """Fake a successful O*NET questions response."""
    body = {
        "start": 1, "end": 30, "total": 30,
        "answer_option": [
            {"value": 1, "name": "Strongly Dislike"},
            {"value": 2, "name": "Dislike"},
            {"value": 3, "name": "Unsure"},
            {"value": 4, "name": "Like"},
            {"value": 5, "name": "Strongly Like"},
        ],
        "question": SAMPLE_QUESTIONS,
    }
    return _fake_response(200, body)


@pytest.fixture
def fake_onet_results():
    """Fake a successful O*NET RIASEC results response."""
    return _fake_response(200, {"result": SAMPLE_RIASEC_RESULTS})


@pytest.fixture
def fake_onet_error():
    """Fake an O*NET API error."""
    return _fake_response(401, {"error": "unauthorized"})


# ---------------------------------------------------------------------------
# Supabase fake client
# ---------------------------------------------------------------------------

SAMPLE_STATS_ROWS = [
    {
        "job_title": "Policy Analyst",
        "count": 450,
        "percent": 0.045,
        "frequency_rank": 12,
        "avg_tenure_days": 912,
        "median_tenure_days": 730,
        "top_transitions": [
            {"next_job_title": "Senior Policy Analyst", "percent": 0.28, "count": 126},
            {"next_job_title": "Program Manager",       "percent": 0.19, "count": 86},
        ],
        "industry": "Government",
        "growth_rate": 0.05,
    },
    {
        "job_title": "Data Analyst",
        "count": 820,
        "percent": 0.082,
        "frequency_rank": 5,
        "avg_tenure_days": 730,
        "median_tenure_days": 638,
        "top_transitions": [
            {"next_job_title": "Data Scientist",  "percent": 0.32, "count": 262},
            {"next_job_title": "Business Analyst", "percent": 0.21, "count": 172},
        ],
        "industry": "Technology",
        "growth_rate": 0.12,
    },
]

SAMPLE_EMBEDDING_ROWS = [
    {"job_id": 1, "title": "Policy Analyst", "description": "Analyzes policy.", "embedding": [0.1, 0.2, 0.3]},
    {"job_id": 2, "title": "Data Analyst",   "description": "Analyzes data.",   "embedding": [0.4, 0.5, 0.6]},
]


def _make_paginated_supabase(rows: list) -> MagicMock:
    """
    Build a mock Supabase client that correctly simulates paginated queries.

    The chain is: client.table(name).select("*").range(start, end).execute()

    First call returns `rows`, second call returns [] to stop pagination.
    """
    client = MagicMock()
    table_mock = MagicMock()
    select_mock = MagicMock()
    range_mock = MagicMock()

    client.table.return_value = table_mock
    table_mock.select.return_value = select_mock
    select_mock.range.return_value = range_mock

    first_page = MagicMock()
    first_page.data = rows
    second_page = MagicMock()
    second_page.data = []
    range_mock.execute.side_effect = [first_page, second_page]

    return client


@pytest.fixture
def mock_supabase_stats():
    """Supabase client pre-loaded with sample stats rows."""
    return _make_paginated_supabase(SAMPLE_STATS_ROWS)


@pytest.fixture
def mock_supabase_embeddings():
    """Supabase client pre-loaded with sample embedding rows."""
    client = MagicMock()
    response = MagicMock()
    response.data = SAMPLE_EMBEDDING_ROWS
    client.table.return_value.select.return_value.limit.return_value.execute.return_value = response
    return client


@pytest.fixture
def mock_supabase():
    """Generic mock Supabase client (for tests that build their own chain)."""
    client = MagicMock()
    table = MagicMock()
    client.table.return_value = table
    return client, table


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_resume_text():
    return (
        "Jane Smith\n"
        "Policy Analyst, U.S. Department of Labor (2018–2024)\n"
        "- Analyzed federal workforce data to support rulemaking\n"
        "- Coordinated with 12 agency stakeholders on compliance reporting\n"
        "Skills: data analysis, policy writing, stakeholder engagement, Excel, SQL"
    )


@pytest.fixture
def sample_experiences():
    return SAMPLE_EXPERIENCES


@pytest.fixture
def sample_jobs():
    return [
        {"job_id": 1, "title": "Policy Analyst", "normalized_title": "policy analyst",
         "description": "Analyzes policy data and produces reports."},
        {"job_id": 2, "title": "Data Analyst",   "normalized_title": "data analyst",
         "description": "Analyzes datasets and builds dashboards."},
    ]


@pytest.fixture
def sample_stats_by_title():
    return {
        "policy analyst": {
            "Percent of Database": 0.045, "Frequency Rank": 12,
            "Avg Tenure (Years)": 2.5, "Median Tenure (Years)": 2.0,
            "Top Transitions": [], "Industry": "Government", "Growth Rate": 0.05,
        },
        "data analyst": {
            "Percent of Database": 0.082, "Frequency Rank": 5,
            "Avg Tenure (Years)": 2.0, "Median Tenure (Years)": 1.75,
            "Top Transitions": [], "Industry": "Technology", "Growth Rate": 0.12,
        },
    }


@pytest.fixture
def sample_vectors():
    return [np.array([0.1, 0.2, 0.3]), np.array([0.4, 0.5, 0.6])]
