# Project Structure

The active codebase lives under `version2/`. The repo root contains legacy files (`app-generic.py`, `usajobs_exploration.py`) and raw data that should not be modified.

```
version2/
├── app/                    # Streamlit UI entry point and components
│   ├── app.py              # Main app (entry point: streamlit run app/app.py)
│   ├── components/         # UI panels (sidebar, job_match, stats, analytics, etc.)
│   └── assets/             # Static assets (CSS, images)
│
├── core/                   # Pure logic, no UI or I/O dependencies
│   ├── embeddings.py       # Vector normalization utilities
│   ├── similarity.py       # Cosine similarity / top-k search
│   ├── stats.py            # Embedding statistics
│   ├── supabase_client.py  # Supabase connection singleton
│   ├── types.py            # Shared type aliases (Vector, Matrix, etc.)
│   ├── models/             # Embedding model loader + provider implementations
│   │   └── embedding_providers/  # base, openai, ollama, cohere, sentence_transformer
│   └── utils/              # text_cleaning, logging, timing
│
├── services/               # Business logic consumed by the UI
│   ├── job_matching.py     # Prepare and rank job match results
│   ├── stats_service.py    # Load/format stats for display
│   ├── resume_extraction_service.py  # LLM-based resume parsing
│   ├── experience_embedding_service.py  # Aggregate experience embeddings
│   ├── prep_service.py     # Load precomputed prep data
│   ├── caching_service.py  # Caching helpers
│   ├── match_explanation_service.py
│   └── visualization_service.py
│
├── prep/                   # Offline pipeline: compute and store embeddings
│   ├── prep_runner.py      # Entry point: python -m prep.prep_runner
│   ├── compute_embeddings.py
│   ├── compute_stats.py
│   └── verify_data.py
│
├── analytics/              # Clustering, seniority normalization, mobility scoring
│
├── schemas/                # Pydantic/dataclass schemas (Job, Embedding, Stats, etc.)
│
├── infra/                  # Config loading and infrastructure setup
│   ├── config.py           # AppConfig (Pydantic), load_settings()
│   ├── settings.toml       # Runtime configuration (provider, model, endpoints)
│   ├── table.sql           # Supabase table definitions
│   └── requirements.txt    # Minimal dependency list
│
├── tracking/               # Session tracking
├── tests/                  # pytest test suite
├── logs/                   # Runtime log files (gitignored)
├── docker/                 # Dockerfile + docker-compose
├── run_app.sh              # Convenience script to launch Streamlit
└── run_prep.sh             # Convenience script to run prep pipeline
```

## Key Conventions

- All new code belongs in `version2/`. Do not modify root-level legacy files.
- `core/` must stay free of UI, I/O, and Supabase dependencies — pure logic only.
- `services/` is the bridge between `core/` and `app/` — business logic lives here.
- `schemas/` holds dataclasses/Pydantic models shared across layers.
- Configuration is always loaded via `infra/config.py:load_settings()` — never read `settings.toml` directly elsewhere.
- Supabase credentials come from environment variables only, never hardcoded.
- New embedding providers go in `core/models/embedding_providers/` and must extend the base class.
- Tests live in `version2/tests/` and are run with `pytest version2/tests/`.
- Python path is set at app startup (`app.py`) to allow `version2/` as the import root — use module-relative imports like `from core.embeddings import ...`.
