#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$BASE_DIR/version2"
VENV_DIR="$APP_DIR/.venv"
REQ_FILE="$BASE_DIR/requirements.txt"
RUN_SCRIPT="$APP_DIR/run_app.sh"

if [[ ! -d "$APP_DIR" ]]; then
  echo "Error: app directory not found: $APP_DIR" >&2
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Error: virtual environment not found: $VENV_DIR" >&2
  echo "Create it first, for example: python3.11 -m venv $VENV_DIR" >&2
  exit 1
fi

if [[ ! -f "$RUN_SCRIPT" ]]; then
  echo "Error: run script not found: $RUN_SCRIPT" >&2
  exit 1
fi

source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip

if [[ -f "$REQ_FILE" ]]; then
  echo "Installing requirements from $REQ_FILE"
  python -m pip install -r "$REQ_FILE"
else
  echo "No requirements.txt found at $REQ_FILE, skipping dependency install"
fi

chmod +x "$RUN_SCRIPT"
cd "$APP_DIR"
exec bash "$RUN_SCRIPT"