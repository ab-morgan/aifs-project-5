"""
cohere_provider.py

Embedding provider for Cohere embedding models.
"""

from __future__ import annotations

import logging
from typing import List

import cohere
from core.models.embedding_model import EmbeddingProvider

logger = logging.getLogger(__name__)


class CohereProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        try:
            self.client = cohere.Client()
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Cohere embedding failed: {e}")
            raise

    def __repr__(self):
        return f"CohereProvider(model={self.model_name})"
