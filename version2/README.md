# Job Match — Version 2

A modular, production‑ready system for resume–job matching using embeddings,
Supabase, and a Streamlit UI.

## Quick Start

1. Install dependencies:
   pip install -r requirements.txt

2. Configure Supabase:
   Edit version2/infra/settings.toml

3. Run the PREP pipeline:
   python -m prep.prep_runner

4. Launch the Streamlit app:
   streamlit run app/app.py

## Architecture

version2/
  app/            Streamlit runtime
  prep/           Embedding + stats pipeline
  core/           Core logic (embeddings, similarity, utils)
  services/       Business logic for UI + runtime
  analytics/      Clustering, seniority, mobility scoring
  infra/          Config + schema
  docker/         Deployment

## Embedding Providers

Supported providers:
- OpenAI
- Ollama (local)
- Cohere
- SentenceTransformer (SBERT, BGE, E5)

Configured in settings.toml:
[embeddings]
provider = "ollama"
model_name = "mxbai-embed-large"

## Prep Pipeline

Generates:
- Cleaned job embeddings
- Global embedding statistics
- Validation of Supabase + schema

## Runtime

The Streamlit app:
- Accepts resume text or file upload
- Generates a resume embedding
- Computes similarity against job embeddings
- Displays top matches + dataset stats

## Docker

Full Docker support under version2/docker/.
