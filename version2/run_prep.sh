#!/usr/bin/env bash
set -e

# Move to repo root, no matter where this script is called from
cd "$(dirname "$0")/.."

APP_ENV="${APP_ENV:-dev}"
ENV_FILE=".env.${APP_ENV}"

# Load the correct .env file so API keys and Supabase credentials are available
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
else
    echo "  Warning: $ENV_FILE not found. Using existing environment variables."
fi

echo ""
echo "  CareerPivots prep pipeline [$APP_ENV]"
echo "  This runs ONCE before starting the app."
echo "  Embeddings and stats will be stored in Supabase."
echo ""

# Pass any extra arguments (e.g. --force) through to prep_runner
python -m prep.prep_runner "$@"
