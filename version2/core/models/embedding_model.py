"""
embedding_model.py

Defines the EmbeddingProvider interface and the factory function
load_embedding_provider(config) that loads the correct provider based
on infra/settings.toml.

This allows the app to switch embedding models without code changes.
"""

from __future__ import annotations

from typing import Any, Dict

from core.models.embedding_providers.openai_provider import OpenAIProvider
from core.models.embedding_providers.ollama_provider import OllamaProvider
from core.models.embedding_providers.sentence_transformer_provider import SentenceTransformerProvider
from core.models.embedding_providers.cohere_provider import CohereProvider


class EmbeddingProvider:
    """Base interface for all embedding providers."""

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError("embed() must be implemented by subclasses")


def load_embedding_provider(config: Dict[str, Any]) -> EmbeddingProvider:
    """
    Factory that loads the correct embedding provider based on config.

    Example settings.toml:

    [embeddings]
    provider = "ollama"
    model_name = "mxbai-embed-large"
    """

    embeddings_cfg = config.get("embeddings", {})
    provider = embeddings_cfg.get("provider")
    model_name = embeddings_cfg.get("model_name")

    if provider == "openai":
        return OpenAIProvider(model_name=model_name)

    if provider == "ollama":
        return OllamaProvider(model_name=model_name)

    if provider == "sentence_transformer":
        return SentenceTransformerProvider(model_name=model_name)

    if provider == "cohere":
        return CohereProvider(model_name=model_name)

    raise ValueError(f"Unknown embedding provider: {provider}")
