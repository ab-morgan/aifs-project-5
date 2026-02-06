"""
openai_provider.py

Embedding provider for OpenAI embedding models.
"""

from __future__ import annotations

import logging
from typing import List

from core.models.embedding_model import EmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name

        try:
            from openai import OpenAI
            self.client = OpenAI()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise

    def __repr__(self):
        return f"OpenAIProvider(model={self.model_name})"
