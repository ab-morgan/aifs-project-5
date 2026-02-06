"""
logging.py

Centralized logging configuration for version2.

This ensures:
- Consistent formatting
- Log files stored under version2/logs/
- Prep and runtime share the same logging style
"""

from __future__ import annotations

import logging
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)


def configure_logging(level: int = logging.INFO):
    """
    Configure global logging for the application.

    Args:
        level (int): Logging level (default: INFO)
    """
    log_path = LOG_DIR / "app.log"

    logging.basicConfig(
        filename=str(log_path),
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Also log to console (useful for Streamlit)
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

    root = logging.getLogger()
    root.addHandler(console)
