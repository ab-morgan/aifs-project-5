import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from core.models.embedding_model import load_embedding_provider


def _make_config(provider="sentence_transformer", model="all-MiniLM-L6-v2"):
    cfg = MagicMock()
    cfg.embeddings.provider = provider
    cfg.embeddings.model_name = model
    cfg.embeddings.batch_size = 8
    cfg.embeddings.normalize = True
    return cfg


def test_load_sentence_transformer_returns_provider():
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    with patch("core.models.embedding_model.SentenceTransformer", return_value=mock_model):
        provider = load_embedding_provider(_make_config())
    assert hasattr(provider, "embed")


def test_sentence_transformer_embed_returns_array():
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    with patch("core.models.embedding_model.SentenceTransformer", return_value=mock_model):
        provider = load_embedding_provider(_make_config())
    result = provider.embed(["test text"])
    assert isinstance(result, np.ndarray)


def test_unknown_provider_raises():
    with patch("core.models.embedding_model.SentenceTransformer"):
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            load_embedding_provider(_make_config(provider="unknown_provider"))
