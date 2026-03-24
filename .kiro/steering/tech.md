# Tech Stack

## Language & Runtime
- Python 3.11+

## Frontend
- Streamlit (UI framework, tabs, sidebar, session state)

## Backend / Data
- Supabase (PostgreSQL + vector storage for job embeddings and stats)
- Pydantic (config models and data validation)
- TOML (configuration via `version2/infra/settings.toml`)

## Embedding Providers (pluggable)
- SentenceTransformers (default: `all-MiniLM-L6-v2`)
- OpenAI
- Ollama (local)
- Cohere

## ML / Data
- NumPy, scikit-learn, scipy (vector math, clustering, similarity)
- pandas (data manipulation)
- torch + transformers + sentence-transformers (local embedding models)

## LLM (Resume Extraction)
- Groq API with `llama-3.1-8b-instant` (OpenAI-compatible endpoint)

## Document Parsing
- pypdf / PyPDF2 (PDF)
- python-docx (DOCX)

## Testing
- pytest (test runner, configured in `version2/pytest.ini`)

## Visualization
- Plotly (charts in analytics dashboard)

## Deployment
- Docker (see `version2/docker/`)

---

## Common Commands

### Run the Streamlit app
```bash
# From repo root
bash version2/run_app.sh
# or directly
streamlit run version2/app/app.py
```

### Run the prep pipeline (precompute embeddings)
```bash
# From version2/
bash version2/run_prep.sh
# or
cd version2 && python -m prep.prep_runner
```

### Run tests
```bash
# From repo root
pytest version2/tests/
# or with verbose output
pytest version2/tests/ -v
```

### Install dependencies
```bash
pip install -r requirements.txt
# or minimal install
pip install -r version2/infra/requirements.txt
```

## Configuration
- All config lives in `version2/infra/settings.toml`
- Supabase credentials are loaded from environment variables: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`
- Embedding provider and model are set under `[embeddings]` in settings.toml
- Resume extraction LLM is set under `[resume_extraction]` in settings.toml
