#!/usr/bin/env bash
set -e

echo "[run_app] Starting Streamlit app..."

# Move to repo root, no matter where this script is called from
cd "$(dirname "$0")/.."

# Launch the Streamlit app
python -m streamlit run version2/app/app.py
