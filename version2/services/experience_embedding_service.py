# version2/app/services/experience_embedding_service.py
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np


def _collect_text_units(experiences: List[Dict[str, Any]]) -> List[str]:
    """
    Flatten experiences into a list of text units to embed.
    Default: use bullets; if no bullets, fall back to job_title + company.
    """
    units: List[str] = []
    for exp in experiences:
        bullets = exp.get("bullets") or []
        for b in bullets:
            b = (b or "").strip()
            if b:
                units.append(b)

        if not bullets:
            title = (exp.get("job_title") or "").strip()
            company = (exp.get("company") or "").strip()
            if title or company:
                units.append(" - ".join([p for p in [title, company] if p]))
    return units


def aggregate_experience_embeddings(
    experiences: List[Dict[str, Any]],
    embedding_provider,
) -> np.ndarray:
    """
    Given structured experiences and an embedding provider with .embed(texts),
    compute a single resume vector by averaging per-experience embeddings.
    """
    text_units = _collect_text_units(experiences)
    if not text_units:
        raise ValueError("No text units found in extracted experiences")

    vectors = embedding_provider.embed(text_units)  # list or array of vectors
    vectors = np.array(vectors)
    if vectors.ndim == 1:
        return vectors

    return vectors.mean(axis=0)
