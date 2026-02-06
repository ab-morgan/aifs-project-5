#!/usr/bin/env bash
set -e

# Optional: sync env vars into settings.toml at runtime if you want
# or just rely on infra/settings.toml directly.

echo "[entrypoint] Running PREP pipeline..."
python -m prep.prep_runner || {
  echo "[entrypoint] PREP failed, but continuing to Streamlit for debugging..."
}

echo "[entrypoint] Starting Streamlit app..."
streamlit run app/app.py
