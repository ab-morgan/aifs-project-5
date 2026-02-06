"""
supabase_client.py

Centralized Supabase client for version2.

Responsibilities:
- Load Supabase URL + service role key from config
- Create a single reusable client instance
- Provide a clean, typed interface for other modules

This module is intentionally stateless and safe for multi-user use.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from infra.config import load_config

try:
    from supabase import create_client, Client
except Exception as e:
    raise ImportError(
        "Supabase client library not installed. "
        "Run: pip install supabase"
    ) from e


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_supabase_client() -> "Client":
    """
    Returns a singleton Supabase client instance.

    Uses LRU cache to ensure:
    - Only one client is created per process
    - Thread-safe reuse
    - No global mutable state

    Returns:
        supabase.Client
    """
    config = load_config()

    url = config.get("supabase", {}).get("url")
    key = config.get("supabase", {}).get("service_role_key")

    if not url or not key:
        raise ValueError(
            "Supabase URL or service_role_key missing in settings.toml "
            "under [supabase]"
        )

    try:
        client = create_client(url, key)
        logger.info("Supabase client initialized successfully.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise


def test_connection() -> bool:
    """
    Simple connectivity test.

    Returns:
        bool: True if Supabase responds, False otherwise.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("jobs").select("*").limit(1).execute()
        return response is not None
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False
