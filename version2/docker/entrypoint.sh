#!/usr/bin/env bash
set -e

APP_ENV="${APP_ENV:-prod}"

echo ""
echo "  CareerPivots container starting (APP_ENV=$APP_ENV)"
echo ""

# Run the prep pipeline to ensure embeddings are up to date.
# If it fails, log the error but continue so Streamlit still starts
# and the admin can diagnose via logs.
echo "  Running prep pipeline..."
cd /app/version2 && python -m prep.prep_runner || {
    echo "  WARNING: prep pipeline failed. Check version2/logs/app.log for details."
}

echo "  Starting Streamlit..."
cd /app
python -m streamlit run version2/app/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --logger.level error
