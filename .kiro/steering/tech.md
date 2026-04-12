# Tech Stack

## Language & Runtime
- Python 3.11+

## Frontend
- Streamlit (UI framework, tabs, sidebar, session state, `@st.dialog` for modals)

## Backend / Data
- Supabase (PostgreSQL + vector storage for job embeddings and stats)
- Pydantic v2 (config models, validation, `@field_validator`)
- TOML (layered config via `settings.toml` + `settings.<env>.toml`)

## Embedding Providers (pluggable)
- SentenceTransformers (default: `all-MiniLM-L6-v2`)
- OpenAI
- Ollama (local)
- Cohere

## ML / Data
- NumPy, scikit-learn, scipy (vector math, clustering, similarity)
- pandas (data manipulation)
- torch + transformers + sentence-transformers (local embedding models)

## LLM (Resume Extraction & Match Explanation)
- Groq API with `llama-3.1-8b-instant` (OpenAI-compatible endpoint)
- Retry logic with flat 1s delay on 429 rate limit errors (up to 4 attempts)

## External APIs
- O*NET Web Services (`https://api-v2.onetcenter.org`) — Mini-IP Interest Profiler
  - Auth: `X-API-Key` header, key in `ONET_API_KEY` env var
  - Endpoints: `/mnm/interestprofiler/questions_30`, `/mnm/interestprofiler/results`

## Document Parsing
- PyPDF2 (PDF)
- python-docx (DOCX)

## Testing
- pytest (configured in `version2/pytest.ini`)

## Visualization
- Plotly (Sankey diagrams, histograms, bar charts)

## Deployment
- Docker (see `version2/docker/`)

## Build / Task Runner
- GNU Make (`Makefile` at repo root)

---

## Common Commands

```bash
make dev       # Start app in development mode (port 8300, debug logging)
make prod      # Start app in production mode (port 8501, errors only)
make prep      # Run the embedding prep pipeline
make test      # Run pytest (single pass)
make lint      # Run ruff linter
make help      # List all targets
```

## Environment System

The app supports two environments controlled by `APP_ENV`:

| Environment | Env file   | Settings override          | Port | Log level |
|-------------|------------|----------------------------|------|-----------|
| `dev`       | `.env.dev` | `settings.dev.toml`        | 8300 | debug     |
| `prod`      | `.env.prod`| `settings.prod.toml`       | 8501 | error     |

Config is loaded by deep-merging `settings.toml` (base) with `settings.<env>.toml` (overrides).
Secrets (API keys, Supabase credentials) always come from the env file, never from TOML.

## Configuration

All config lives in `version2/infra/`. Key sections in `settings.toml`:

| Section             | Purpose                                      |
|---------------------|----------------------------------------------|
| `[embeddings]`      | Provider, model name, batch size, normalize  |
| `[resume_extraction]` | Groq model, endpoint                       |
| `[ui]`              | App name, logo size, font sizes, colors      |
| `[limits]`          | `max_resume_chars`, `max_upload_mb`          |
| `[app]`             | `env`, `debug` (set in env-specific TOML)    |
| `[server]`          | `port`, `log_level` (set in env-specific TOML)|

Config is loaded via `infra/config.py:load_settings()` — never read TOML files directly elsewhere.
Supabase credentials: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` env vars.

## Logging

- `ERROR+` → `version2/logs/app.log` (file only, with filename + line number)
- Terminal → startup URL only (all other output suppressed)
- Configured in `core/utils/logging.py:configure_logging()`
- Called at the very top of `app.py` before any other imports

## Security Conventions

- All database-sourced strings rendered in HTML must be passed through `html.escape()`
- CSS values from `settings.toml` are validated by Pydantic before injection
- Resume input is sanitized (control chars stripped) before processing
- API error response bodies are logged internally, never surfaced to the UI
- `ONET_API_KEY` raises immediately if missing or set to placeholder value
