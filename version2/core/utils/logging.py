"""
logging.py

Centralized logging configuration for version2.

Behaviour:
- ERROR and above  → version2/logs/app.log (file only)
- WARNING and below → suppressed from terminal
- Startup/shutdown messages → printed directly via print() so they always
  appear in the terminal regardless of log level filters
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_PATH = LOG_DIR / "app.log"


def configure_logging():
    """
    Wire up logging so that:
    - All ERROR+ records go to app.log with full context
    - The terminal receives nothing from the logging system
      (startup messages are printed directly instead)
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # capture everything at root level

    # Remove any handlers that Streamlit or other libs may have added
    root.handlers.clear()

    # ── File handler: ERROR and above ──────────────────────
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(file_handler)

    # ── Null handler for everything else (no terminal noise) ─
    null_handler = logging.NullHandler()
    root.addHandler(null_handler)

    # Silence noisy third-party loggers that spam at INFO/WARNING
    for noisy in ("httpx", "httpcore", "urllib3", "sentence_transformers",
                  "transformers", "torch", "supabase", "postgrest"):
        logging.getLogger(noisy).setLevel(logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Errors go to app.log automatically."""
    return logging.getLogger(name)
