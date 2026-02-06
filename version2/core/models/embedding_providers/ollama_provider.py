"""
ollama_provider.py

Embedding provider for local Ollama models.
"""

from __future__ import annotations

import logging
import requests
from typing import List

from core.models.embedding_model import EmbeddingProvider

logger = logging.getLogger(__name__)


class OllamaProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.url = "http://localhost:11434/api/embeddings"

    def embed(self, text: str) -> List[float]:
        try:
            payload = {"model": self.model_name, "prompt": text}
            response = requests.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise

    def __repr__(self):
        return f"OllamaProvider(model={self.model_name})"
