#!/usr/bin/env bash
set -e

echo "[run_app] Starting Streamlit runtime..."

# Optional: activate venv if you use one
# source .venv/bin/activate

streamlit run version2/app/app.py
