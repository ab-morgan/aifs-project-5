# Services Layer

Contains business logic used by the runtime.

Modules:

job_matching.py
  Joins similarity results with job metadata.
  Sorts and formats rows for UI.

stats_service.py
  Loads global stats from Supabase.
  Prepares them for sidebar display.

caching_service.py
  Streamlit caching for jobs, embeddings, stats.

Purpose:
Keeps UI clean and separates concerns.
