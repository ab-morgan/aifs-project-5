"""
embedding_model.py

Defines the EmbeddingProvider interface and the factory function
load_embedding_provider(config) that loads the correct provider based
on infra/settings.toml.

This allows the app to switch embedding models without code changes.
"""

from __future__ import annotations

from typing import Any
from sentence_transformers import SentenceTransformer
import numpy as np


def load_embedding_provider(config: Any):
    """
    Load the embedding provider using the new AppConfig structure.
    Supports:
    - config.embeddings.provider
    - config.embeddings.model_name
    - config.embeddings.batch_size
    - config.embeddings.normalize
    """

    # If config is a dict (legacy), normalize it
    if isinstance(config, dict):
        embeddings_cfg = config.get("embeddings", {})
        provider = embeddings_cfg.get("provider")
        model_name = embeddings_cfg.get("model_name")
        batch_size = embeddings_cfg.get("batch_size", 128)
        normalize = embeddings_cfg.get("normalize", True)

    else:
        # New Pydantic AppConfig
        provider = config.embeddings.provider
        model_name = config.embeddings.model_name
        batch_size = config.embeddings.batch_size
        normalize = config.embeddings.normalize

    # -----------------------------
    # SentenceTransformer provider
    # -----------------------------
    if provider == "sentence_transformer":
        model = SentenceTransformer(model_name)

        class STProvider:
            def embed(self, texts):
                if isinstance(texts, str):
                    texts = [texts]
                vectors = model.encode(texts, batch_size=batch_size)
                if normalize:
                    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
                return vectors

        return STProvider()

    # -----------------------------
    # Add other providers here
    # -----------------------------
    raise ValueError(f"Unknown embedding provider: {provider}")
