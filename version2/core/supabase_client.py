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
import os
from functools import lru_cache

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

    Reads: 
    - SUPABASE_URL 
    - SUPABASE_SERVICE_ROLE_KEY 
    """ 
    url = os.getenv("SUPABASE_URL") 
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY") 
    if not url or not key: 
        raise ValueError( 
            "Environment variables SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY " 
            "must be set." 
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
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("jobhop_raw").select("*").limit(1).execute()
        return response is not None
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False
