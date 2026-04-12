#!/usr/bin/env bash
set -e

# Move to repo root, no matter where this script is called from
cd "$(dirname "$0")/.."

LOG_FILE="version2/logs/app.log"
PORT=8300

echo ""
echo "  CareerPivots — starting on port $PORT"
echo "  Errors will be logged to: $LOG_FILE"
echo ""

# Run Streamlit, filtering its output:
#   - Keep lines that indicate the server URL (startup success)
#   - Keep lines that indicate a fatal startup error
#   - Suppress everything else (INFO chatter, warnings, library noise)
python -m streamlit run version2/app/app.py \
    --server.port $PORT \
    --logger.level error \
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
