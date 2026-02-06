import pytest
from unittest.mock import MagicMock
import numpy as np


@pytest.fixture
def mock_supabase():
    client = MagicMock()
    table = MagicMock()
    client.table.return_value = table
    return client, table


@pytest.fixture
def sample_jobs():
    return [
        {"id": 1, "title": "Data Scientist"},
        {"id": 2, "title": "ML Engineer"},
    ]


@pytest.fixture
def sample_embeddings():
    return [
        {"job_id": 1, "embedding": np.array([0.1, 0.2, 0.3])},
        {"job_id": 2, "embedding": np.array([0.4, 0.5, 0.6])},
    ]


@pytest.fixture
def sample_resume_text():
    return "Experienced data scientist with strong Python skills."
