from services.job_matching import prepare_job_matches, normalize_title


def _make_jobs():
    return [
        {"job_id": 1, "title": "Data Scientist", "normalized_title": "data scientist", "description": "Analyzes data."},
        {"job_id": 2, "title": "ML Engineer",    "normalized_title": "ml engineer",    "description": "Builds models."},
    ]


def _make_stats():
    return {
        "data scientist": {"Percent of Database": 0.05, "Frequency Rank": 3,
                           "Avg Tenure (Years)": 2.5, "Median Tenure (Years)": 2.0,
                           "Top Transitions": [], "Industry": "Tech", "Growth Rate": 0.1},
    }


def test_prepare_job_matches_length():
    matches = [(0, 0.9), (1, 0.8)]   # (index, similarity) tuples
    rows = prepare_job_matches(matches, _make_jobs(), _make_stats())
    assert len(rows) == 2


def test_prepare_job_matches_title():
    matches = [(0, 0.9)]
    rows = prepare_job_matches(matches, _make_jobs(), _make_stats())
    assert rows[0]["title"] == "Data Scientist"


def test_prepare_job_matches_similarity_scaled():
    matches = [(0, 0.9)]
    rows = prepare_job_matches(matches, _make_jobs(), _make_stats())
    # similarity is stored as a percentage (0–100)
    assert rows[0]["similarity"] == 90.0


def test_prepare_job_matches_stats_populated():
    matches = [(0, 0.9)]
    rows = prepare_job_matches(matches, _make_jobs(), _make_stats())
    assert rows[0]["stats"]["frequency_rank"] == 3


def test_prepare_job_matches_missing_stats():
    matches = [(1, 0.8)]   # ML Engineer has no stats entry
    rows = prepare_job_matches(matches, _make_jobs(), _make_stats())
    assert rows[0]["stats"]["percent_of_db"] is None


def test_normalize_title():
    assert normalize_title("  Data Scientist  ") == "data scientist"
