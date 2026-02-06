# Core Layer

Contains the fundamental logic of the system.

Modules:

Embedding Providers:
  embedding_model.py (factory + interface)
  embedding_providers/ (OpenAI, Ollama, Cohere, SBERT)

Similarity:
  similarity.py (cosine similarity + top-k search)

Embeddings Utils:
  embeddings.py (normalization + validation)

Supabase:
  supabase_client.py (singleton client)

Utils:
  text_cleaning.py
  timing.py
  logging.py

Errors:
  errors.py (custom exceptions)

Types:
  types.py (shared type aliases)

Purpose:
Pure, deterministic, reusable across prep + runtime.
