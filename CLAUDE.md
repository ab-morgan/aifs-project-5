# CareerPivots — CLAUDE.md

## Project Overview

CareerPivots matches a resume against O*NET job types using semantic similarity.
The pipeline: resume text → Groq LLM extracts structured experiences → sentence-transformers embeds them → cosine similarity against precomputed O*NET job vectors in Supabase → top-k matches enriched with labour-market stats (tenure, transitions, frequency rank).

There are two running interfaces:

| Interface | Stack | Port |
|-----------|-------|------|
| Legacy Streamlit app | Python / Streamlit | 8501 |
| React frontend (current) | Vite + React + Tailwind v4 | 5173 |
| FastAPI backend (new) | FastAPI / uvicorn | 8000 |

Both interfaces share the exact same Python service layer. **Do not modify existing files in `version2/services/` or `version2/core/`.**

---

## Repository Layout

```
aifs-project-5/
├── version2/                   # Python backend (services + Streamlit app)
│   ├── api/                    # NEW — FastAPI layer
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app: POST /api/match, GET /api/health
│   │   └── requirements.txt    # fastapi, uvicorn[standard], python-multipart
│   ├── app/                    # Streamlit app (do not break)
│   │   └── app.py
│   ├── core/                   # Utilities (do not modify)
│   │   ├── similarity.py       # compute_top_k()
│   │   ├── supabase_client.py  # get_supabase_client()
│   │   └── models/
│   │       └── embedding_model.py  # load_embedding_provider()
│   ├── services/               # Business logic (do not modify)
│   │   ├── resume_extraction_service.py   # extract_experiences() via Groq
│   │   ├── experience_embedding_service.py # aggregate_experience_embeddings()
│   │   ├── job_matching.py     # prepare_job_matches()
│   │   ├── match_explanation_service.py   # explain_match() via Groq
│   │   ├── prep_service.py     # load_embeddings_cached(), load_stats_cached()
│   │   └── stats_service.py    # load_stats_for_display()
│   ├── infra/
│   │   ├── config.py           # AppConfig + load_settings()
│   │   └── settings.toml       # Base config (embeddings, resume_extraction, ui, limits)
│   └── docker/
│       ├── docker-compose.yml  # All three services
│       ├── Dockerfile.app      # Streamlit container
│       ├── Dockerfile.api      # FastAPI container (NEW)
│       └── entrypoint.sh       # Runs prep pipeline then Streamlit
├── frontend/                   # React frontend (NEW)
│   ├── src/
│   │   ├── main.tsx            # Entry point
│   │   ├── api/
│   │   │   └── client.ts       # fetchMatches() — POST /api/match
│   │   ├── app/
│   │   │   ├── App.tsx         # Root component — state + API call
│   │   │   └── components/
│   │   │       ├── SearchSidebar.tsx       # Resume input, preferences, match count
│   │   │       ├── JobResults.tsx          # Results list + export toolbar
│   │   │       ├── JobResultCard.tsx       # Card + JobMatch interface definition
│   │   │       ├── InterestQuestionnaire.tsx # O*NET interest profiler dialog
│   │   │       ├── JobPreferences.tsx
│   │   │       ├── ResumeInput.tsx
│   │   │       └── ui/                    # Full shadcn/ui component set
│   │   └── styles/
│   │       ├── index.css       # Imports fonts, tailwind, theme
│   │       ├── tailwind.css    # Tailwind v4 source directive
│   │       └── theme.css       # CSS variables (colors, radius, typography)
│   ├── package.json
│   ├── vite.config.ts          # Tailwind v4 plugin + /api proxy to :8000
│   └── Dockerfile              # Multi-stage: Vite build → serve static
└── .env.prod                   # Secrets — never committed
```

---

## Environment Variables

Required in `.env` / `.env.prod`:

```
SUPABASE_URL=https://...supabase.co
SUPABASE_PUBLISHABLE_KEY=eyJ...   # anon/public key, NOT service role
GROQ_API_KEY=gsk_...
APP_ENV=dev                        # or prod
```

`load_settings()` in `version2/infra/config.py` merges `settings.toml` + `settings.{APP_ENV}.toml` then reads the three secret vars from the environment.

---

## Running Locally

### FastAPI backend

```bash
# From the project root
PYTHONPATH=version2 uvicorn version2.api.main:app --reload --port 8000
```

First request after a cold start is slow (sentence-transformers loads, then Supabase fetches all embeddings + stats — both are `lru_cache`'d after that).

### React frontend (Vite dev server)

```bash
cd frontend
npm run dev          # http://localhost:5173
```

Vite proxies `/api/*` → `http://localhost:8000`, so no CORS issues in development.

### Streamlit app (legacy — still works independently)

```bash
cd version2
streamlit run app/app.py --server.port 8501
```

---

## Docker

```bash
cd version2/docker
docker compose up --build
```

Services:

| Container | Port | Notes |
|-----------|------|-------|
| `careerpivots-api` | 8000 | FastAPI; health-check before frontend starts |
| `careerpivots-frontend` | 5173 | Serves static Vite build via `serve` |
| `careerpivots` | 8501 | Original Streamlit app |

Secrets are loaded from `../../.env.prod` (relative to `version2/docker/`).

The FastAPI container sets `PYTHONPATH=/app/version2` so service/core/infra packages resolve without a `version2.` prefix.

---

## Key Data Flow (FastAPI path)

```
POST /api/match
  { resume_text, preferences, exclusions, match_count }
        │
        ▼
extract_experiences(resume_text, cfg.resume_extraction)
  → Groq llama-3.1-8b-instant returns structured JSON
  → List[{job_title, company, bullets, skills, ...}]
        │
        ▼
aggregate_experience_embeddings(experiences, embedding_provider)
  → sentence-transformers all-MiniLM-L6-v2
  → np.ndarray shape (384,)
        │
        ▼
_load_embeddings()  [lru_cache — Supabase jobhop_embeddings]
_load_stats()       [lru_cache — Supabase jobhop_stats_mv via load_stats_for_display()]
        │
        ▼
compute_top_k(resume_vector, job_vectors, top_k=match_count)
  → List[(job_index, cosine_similarity)]
        │
        ▼
prepare_job_matches(matches, jobs, stats_by_title)
  → List[{title, description, similarity (0–100), stats}]
        │
        ▼
explain_match(experiences, job, cfg.resume_extraction)  [per match, Groq]
  → 2-3 sentence explanation string
        │
        ▼
Response: List[JobMatch]  (camelCase, nullable insight fields)
```

### Known quirk — stats lookup

`stats_service.load_stats_for_display()` keys the stats dict by the raw `job_title` string (mixed case). `prepare_job_matches()` looks up by `normalize_title(title)` (lowercase). These rarely match, so `insights.percentOfDatabase / frequencyRank / averageTenure / medianTenure` are often `null` on real API responses. `JobResultCard.tsx` renders `"—"` for null values. This is a pre-existing issue in the service layer; do not attempt to fix it by modifying the service files.

---

## API Contract

### `GET /api/health`
```json
{ "status": "ok" }
```

### `POST /api/match`
Request:
```json
{
  "resume_text": "string (required)",
  "preferences": "string (optional)",
  "exclusions": "string (optional)",
  "match_count": 10
}
```
Response: `JobMatch[]`
```json
[{
  "id": "uuid",
  "jobTitle": "string",
  "jobDescription": "string",
  "matchPercentage": 87.3,
  "matchReason": "string",
  "insights": {
    "percentOfDatabase": 1.43 | null,
    "frequencyRank": 28 | null,
    "averageTenure": 3.9 | null,
    "medianTenure": 3.2 | null,
    "topTransitions": [{ "jobTitle": "string", "percentage": 26.3 }]
  }
}]
```

---

## Frontend — Wiring Notes

- **`src/api/client.ts`** — typed `fetchMatches()`. `VITE_API_URL` env var overrides the base URL (used in Docker; empty string in dev so the Vite proxy handles routing).
- **`src/app/App.tsx`** — the only file that calls the API. All other components receive data via props and remain mock-free.
- **`src/app/components/JobResultCard.tsx`** — exports the `JobMatch` TypeScript interface used by the whole frontend.
- The O*NET interest questionnaire (`InterestQuestionnaire.tsx`) is local state only — scores are stored in `interestProfile` in `App.tsx` but not sent to the API.

---

## Supabase Tables

| Table / View | Used by |
|---|---|
| `jobhop_embeddings` | `_load_embeddings()` in `version2/api/main.py` |
| `jobhop_stats_mv` | `load_stats_for_display()` → `_load_stats()` |
| `jobhop_raw` | Prep pipeline only |

---

## Constraints

- **Never modify** files in `version2/services/` or `version2/core/`.
- **Never break** `version2/app/app.py` — the Streamlit app must still run.
- New Python code belongs in `version2/api/`.
- New frontend code belongs in `frontend/src/`.
- Python 3.11+, FastAPI ≥ 0.110, uvicorn, Vite 6, Tailwind v4.
