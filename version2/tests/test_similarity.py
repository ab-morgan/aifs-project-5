import numpy as np
import pytest
from core.similarity import cosine_similarity, compute_top_k


def test_cosine_similarity_identical():
    a = np.array([1.0, 0.0])
    b = np.array([1.0, 0.0])
    assert cosine_similarity(a, b) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    a = np.array([0.0, 0.0])
    b = np.array([1.0, 0.0])
    assert cosine_similarity(a, b) == 0.0


def test_compute_top_k_returns_correct_count():
    vecs = [np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([0.5, 0.5])]
    query = np.array([1.0, 0.0])
    results = compute_top_k(query, vecs, top_k=2)
    assert len(results) == 2


def test_compute_top_k_sorted_descending():
    vecs = [np.array([0.0, 1.0]), np.array([1.0, 0.0])]
    query = np.array([1.0, 0.0])
    results = compute_top_k(query, vecs, top_k=2)
    # results are (index, score) tuples — best match first
    assert results[0][1] >= results[1][1]


def test_compute_top_k_empty_vectors():
    results = compute_top_k(np.array([1.0, 0.0]), [], top_k=5)
    assert results == []
