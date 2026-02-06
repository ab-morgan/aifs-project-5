import numpy as np
from core.similarity import cosine_similarity, compute_top_k


def test_cosine_similarity():
    a = np.array([1, 0])
    b = np.array([1, 0])
    assert cosine_similarity(a, b) == 1.0


def test_compute_top_k(sample_embeddings):
    resume_vec = np.array([0.1, 0.2, 0.3])
    results = compute_top_k(resume_vec, sample_embeddings, top_k=1)
    assert len(results) == 1
    assert "job_id" in results[0]
