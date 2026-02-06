#!/usr/bin/env bash
set -e

echo "[run_prep] Running PREP pipeline..."

# Optional: activate venv if you use one
# source .venv/bin/activate

python -m version2.prep.prep_runner
