from services.job_matching import prepare_job_matches


def test_prepare_job_matches(sample_jobs):
    matches = [
        {"job_id": 1, "score": 0.9},
        {"job_id": 2, "score": 0.8},
    ]

    rows = prepare_job_matches(matches, sample_jobs)
    assert len(rows) == 2
    assert rows[0]["title"] == "Data Scientist"
