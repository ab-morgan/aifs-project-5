# Infra Layer

Contains:
- settings.toml (global configuration)
- config.py (config loader + validation)
- table.sql (Supabase schema)

Configuration file:
version2/infra/settings.toml

Required sections:
[supabase]
url = "..."
service_role_key = "..."

[embeddings]
provider = "ollama"
model_name = "mxbai-embed-large"
batch_size = 16
normalize = true

Schema:
table.sql defines jobs, job_embeddings, job_stats.
Run it in the Supabase SQL editor.
