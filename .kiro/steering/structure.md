# Project Structure

The active codebase lives under `version2/`. The repo root contains legacy files (`app-generic.py`, `usajobs_exploration.py`) and raw data — do not modify those.

```
repo root/
├── Makefile                        # Dev/prod task runner (make dev, make prod, make test)
├── .env.dev                        # Dev secrets — gitignored, copy from .env.template
├── .env.prod                       # Prod secrets — gitignored, copy from .env.template
├── .env.template                   # Template showing required env vars (committed)
│
└── version2/
    ├── app/                        # Streamlit UI entry point and components
    │   ├── app.py                  # Main entry point: streamlit run version2/app/app.py
    │   ├── components/
    │   │   ├── sidebar.py          # Resume upload/paste, RIASEC display, preferences
    │   │   ├── job_match_panel.py  # Job match cards, export, select-all
    │   │   ├── onet_wizard.py      # @st.dialog modal for O*NET Mini-IP questionnaire
    │   │   ├── stats_panel.py      # Job market statistics tab
    │   │   ├── analytics_dashboard.py
    │   │   ├── sankey_panel.py
    │   │   ├── transition_explorer.py
    │   │   └── dashboard_panel.py  # Tracking events dashboard (optional)
    │   └── assets/
    │       ├── styles.css          # CSS using custom properties (--body-font-size, etc.)
    │       └── Copilot1.png        # App logo
    │
    ├── core/                       # Pure logic — no UI, no Supabase, no I/O
    │   ├── embeddings.py           # Vector normalization utilities
    │   ├── similarity.py           # Cosine similarity / top-k search
    │   ├── stats.py                # Embedding statistics
    │   ├── supabase_client.py      # Supabase singleton (lru_cache)
    │   ├── types.py                # Shared type aliases
    │   ├── cache.py                # In-process memoization helpers
    │   ├── errors.py               # Custom exception classes
    │   ├── models/
    │   │   ├── embedding_model.py  # load_embedding_provider() factory
    │   │   └── embedding_providers/  # base, openai, ollama, cohere, sentence_transformer
    │   └── utils/
    │       ├── logging.py          # configure_logging(), get_logger() — call first in app.py
    │       ├── text_cleaning.py    # clean_text() for embedding normalization
    │       └── timing.py           # time_block() context manager
    │
    ├── services/                   # Business logic — bridge between core and UI
    │   ├── job_matching.py         # prepare_job_matches(), normalize_title()
    │   ├── stats_service.py        # load_stats_for_display(), paginated Supabase fetch
    │   ├── resume_extraction_service.py  # Groq LLM resume parser
    │   ├── experience_embedding_service.py  # Aggregate experience embeddings
    │   ├── match_explanation_service.py  # Groq LLM match explanation + retry logic
    │   ├── onet_service.py         # O*NET API: fetch_questions(), fetch_results()
    │   ├── prep_service.py         # load_prep_data() — cached Supabase loader
    │   ├── caching_service.py      # st.cache_data wrappers
    │   └── visualization_service.py  # Plotly chart builders
    │
    ├── prep/                       # Offline pipeline: compute and store embeddings
    │   ├── prep_runner.py          # Entry point: python -m prep.prep_runner
    │   ├── compute_embeddings.py
    │   ├── compute_stats.py
    │   └── verify_data.py
    │
    ├── analytics/                  # Clustering, seniority normalization, mobility scoring
    │
    ├── schemas/                    # Pydantic/dataclass schemas (Job, Embedding, Stats, etc.)
    │
    ├── infra/                      # Config loading and infrastructure
    │   ├── config.py               # AppConfig, load_settings(), get_app_env()
    │   ├── settings.toml           # Base config (committed, no secrets)
    │   ├── settings.dev.toml       # Dev overrides: debug=true, port 8300, relaxed limits
    │   ├── settings.prod.toml      # Prod overrides: debug=false, port 8501, strict limits
    │   ├── table.sql               # Supabase table definitions
    │   └── requirements.txt        # Minimal dependency list
    │
    ├── tracking/                   # Session ID + event logging to Supabase
    ├── tests/                      # pytest test suite
    ├── logs/                       # Runtime log files — gitignored
    ├── docker/                     # Dockerfile + docker-compose
    ├── run_app.sh                  # Called by Makefile; sources .env.<env>, starts Streamlit
    └── run_prep.sh                 # Runs the prep pipeline
```

## Key Conventions

- All new code belongs in `version2/`. Do not modify root-level legacy files.
- `core/` must stay free of UI, Streamlit, and Supabase dependencies — pure logic only.
- `services/` is the bridge between `core/` and `app/` — business logic lives here.
- `schemas/` holds dataclasses/Pydantic models shared across layers.
- Config is always loaded via `infra/config.py:load_settings()`. Never read TOML files directly.
- Secrets come from `.env.dev` / `.env.prod` only — never hardcoded or in TOML.
- New embedding providers go in `core/models/embedding_providers/` and must extend `EmbeddingProvider`.
- Tests live in `version2/tests/` — run with `make test`.
- `configure_logging()` must be called at the very top of `app.py` before any other imports.
- All database-sourced strings rendered into `unsafe_allow_html` blocks must be wrapped in `html.escape()`.
- CSS values injected from config are validated by Pydantic `@field_validator` before use.
- The active environment is set by `APP_ENV` env var (`dev` or `prod`). Use `config.is_dev` / `config.is_prod` in code.
- Resume input is sanitized (control chars stripped) before any processing.
- The O*NET attribution footer must remain visible in the app at all times (terms of service requirement).
