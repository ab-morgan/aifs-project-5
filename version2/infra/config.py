"""
config.py

Central configuration loader for version2.

Loads settings from:
    infra/settings.toml

Provides:
    load_config()  -> returns a validated config dict

Design:
- Cached so it loads once per process
- Validates required sections (supabase, embeddings)
- Raises clear errors when config is missing or malformed
"""

from __future__ import annotations

import toml
import logging
from functools import lru_cache
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

SETTINGS_PATH = Path(__file__).parent / "settings.toml"


REQUIRED_SECTIONS = {
    "supabase": ["url", "service_role_key"],
    "embeddings": ["provider", "model_name"],
}


def _validate_config(cfg: Dict[str, Any]) -> None:
    """
    Validate required sections and keys exist.
    Raises ValueError on missing fields.
    """
    for section, keys in REQUIRED_SECTIONS.items():
        if section not in cfg:
            raise ValueError(f"Missing required config section: [{section}]")

        for key in keys:
            if key not in cfg[section]:
                raise ValueError(
                    f"Missing required key '{key}' in [{section}] section of settings.toml"
                )


@lru_cache(maxsize=1)
def load_config() -> Dict[str, Any]:
    """
    Load and validate settings.toml.

    Returns:
        dict: Parsed and validated configuration.

    Raises:
        FileNotFoundError: If settings.toml is missing.
        ValueError: If required fields are missing.
    """
    if not SETTINGS_PATH.exists():
        raise FileNotFoundError(
            f"settings.toml not found at: {SETTINGS_PATH}. "
            "Ensure the file exists in version2/infra/"
        )

    try:
        cfg = toml.load(SETTINGS_PATH)
    except Exception as e:
        logger.error(f"Failed to parse settings.toml: {e}")
        raise

    # Validate required structure
    _validate_config(cfg)

    logger.info("Configuration loaded and validated successfully.")
    return cfg
