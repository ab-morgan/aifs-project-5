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
# ── Typical dev startup sequence ─────────────────────────────────────────
make prep-dev    # STEP 1: compute embeddings + stats into dev Supabase
make dev         # STEP 2: start app in dev mode (port 8300, debug logging)

# ── Typical prod startup sequence ────────────────────────────────────────
make prep-prod   # STEP 1: compute embeddings + stats into prod Supabase
make prod        # STEP 2: start app in prod mode (port 8501, errors only)

# ── Force recompute (after job data changes) ──────────────────────────────
make prep-dev-force   # recompute all dev embeddings + stats
make prep-prod-force  # recompute all prod embeddings + stats

# ── Other targets ─────────────────────────────────────────────────────────
make test        # Run pytest (all external services mocked — no keys needed)
make test-prep   # Run only the prep pipeline tests
make lint        # Run ruff linter
make help        # List all targets with descriptions
```

## Prep → App Workflow

The system has two distinct phases:

### Phase 1 — Prep (run once, offline)
`make prep-dev` or `make prep-prod` runs `version2/prep/prep_runner.py` which:
1. Reads `[prep]` config from `settings.<env>.toml` (batch size, skip logic, source table)
2. Verifies Supabase connectivity and required tables
3. Fetches raw job data from `jobhop_raw`
4. Computes embeddings via the configured provider → stores in `jobhop_embeddings`
5. Computes per-title statistics (count, tenure, transitions, etc.) → stores in `jobhop_stats`

Dev prep uses smaller batches and verbose logging. Prod prep uses full batches and errors-only logging.
Both are **idempotent** — they skip steps where data already exists.
Use `make prep-dev-force` / `make prep-prod-force` to recompute everything from scratch.

### Phase 2 — Runtime (app serving users)
`make dev` / `make prod` starts the Streamlit app. On first request:
- `prep_service.load_embeddings_cached()` fetches embeddings from Supabase → stores in process-level cache (`core/cache.py`)
- `prep_service.load_stats_cached()` fetches stats from Supabase → stores in process-level cache

All subsequent users are served from the in-process cache — Supabase is **not queried again** until the process restarts. This means:
- Fast response for all users after the first load
- No repeated database queries for static job data
- Cache survives across Streamlit sessions on the same server process

If the app starts and finds no embeddings (prep hasn't been run), it displays a warning and stops.

To refresh the cache after re-running prep, restart the app process.

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
