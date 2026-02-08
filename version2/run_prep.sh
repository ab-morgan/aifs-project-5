#!/usr/bin/env bash
set -e

echo "[run_prep] Running PREP pipeline..."

# Always run from the directory where this script lives
cd "$(dirname "$0")"

python -m prep.prep_runner
