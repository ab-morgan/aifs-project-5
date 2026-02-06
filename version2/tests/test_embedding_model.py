from unittest.mock import patch
from core.models.embedding_model import load_embedding_provider


def test_load_embedding_provider_openai():
    config = {"provider": "openai", "model_name": "text-embedding-3-small"}
    with patch("core.models.embedding_model.OpenAIEmbedding") as mock_cls:
        load_embedding_provider(config)
        mock_cls.assert_called_once()
