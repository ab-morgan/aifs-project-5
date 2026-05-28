#!/usr/bin/env bash
set -e

# Move to repo root, no matter where this script is called from
cd "$(dirname "$0")/.."

# APP_ENV must be set before calling this script (done by Makefile targets).
# Default to dev if called directly.
APP_ENV="${APP_ENV:-dev}"
ENV_FILE=".env.${APP_ENV}"
LOG_FILE="version2/logs/app.log"

# Load the correct .env file
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
else
    echo "  Warning: $ENV_FILE not found. Using existing environment variables."
fi

# Derive port and log level from APP_ENV
if [ "$APP_ENV" = "prod" ]; then
    PORT=8501
    STREAMLIT_LOG_LEVEL="error"
else
    PORT=8300
    STREAMLIT_LOG_LEVEL="debug"
fi

echo ""
echo "  CareerPivots [$APP_ENV] — starting on port $PORT"
echo "  Errors will be logged to: $LOG_FILE"
echo ""

python -m streamlit run version2/app/app.py \
    --server.port "$PORT" \
    --logger.level "$STREAMLIT_LOG_LEVEL" \
    2>&1 | awk '
        /Local URL|Network URL|You can now view|stopped with exit code [^0]|Error|Traceback/ {
            print
        }
    '

EXIT_CODE=${PIPESTATUS[0]}
if [ "$EXIT_CODE" -ne 0 ]; then
    echo ""
    echo "  App exited with error (code $EXIT_CODE). Check $LOG_FILE for details."
    echo ""
    exit $EXIT_CODE
fi
