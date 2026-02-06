"""
sentence_transformer_provider.py

Embedding provider for SentenceTransformer models (SBERT, BGE, E5, etc.).
"""

from __future__ import annotations

import logging
from typing import List

from sentence_transformers import SentenceTransformer
from core.models.embedding_model import EmbeddingProvider

logger = logging.getLogger(__name__)


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model '{model_name}': {e}")
            raise

    def embed(self, text: str) -> List[float]:
        try:
            vector = self.model.encode(text, normalize_embeddings=False)
            return vector.tolist()
        except Exception as e:
            logger.error(f"SentenceTransformer embedding failed: {e}")
            raise

    def __repr__(self):
        return f"SentenceTransformerProvider(model={self.model_name})"
