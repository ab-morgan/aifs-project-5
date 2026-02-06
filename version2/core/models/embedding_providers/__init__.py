"""
Makes embedding providers importable as a package.
"""

from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .sentence_transformer_provider import SentenceTransformerProvider
from .cohere_provider import CohereProvider

__all__ = [
    "OpenAIProvider",
    "OllamaProvider",
    "SentenceTransformerProvider",
    "CohereProvider",
]
