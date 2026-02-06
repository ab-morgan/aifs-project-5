# PREP Pipeline

The PREP pipeline prepares all data required for the runtime app.

Steps:

1. verify_data
   Ensures Supabase is reachable, tables exist, and embedding config is valid.

2. compute_embeddings
   Loads raw job descriptions, cleans text, generates embeddings, uploads to Supabase.

3. compute_stats
   Computes vector norms, global embedding distribution, and uploads stats.

4. prep_runner
   Orchestrates all steps. Idempotent and safe to re-run.

Run the pipeline:
python -m prep.prep_runner

Output tables:
- job_embeddings
- job_stats
