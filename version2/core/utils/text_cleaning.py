"""
text_cleaning.py

Provides lightweight, deterministic text‑cleaning utilities used by:
- compute_embeddings (prep)
- resume processing (runtime)
- analytics

The goal is NOT heavy NLP preprocessing — just enough normalization
to ensure embeddings are stable and consistent.
"""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """
    Normalize text for embedding generation.

    Steps:
    - Lowercase
    - Remove extra whitespace
    - Strip control characters
    - Normalize punctuation spacing

    Args:
        text (str): Raw input text.

    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove control characters
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
