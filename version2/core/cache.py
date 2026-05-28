"""
cache.py

A simple, process-local in-memory cache for backend use.
This is NOT used in Streamlit runtime (which uses st.cache_data).

Use cases:
- Caching model instances
- Caching expensive computations during prep
- Avoiding repeated Supabase fetches in analytics scripts
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable


def memoize(maxsize: int = 32) -> Callable:
    """
    Decorator for lightweight memoization.

    Example:
        @memoize()
        def expensive_fn(x):
            ...
    """
    def wrapper(fn: Callable) -> Callable:
        return lru_cache(maxsize=maxsize)(fn)
    return wrapper


# Global cache for arbitrary objects
_GLOBAL_CACHE = {}


def set_cache(key: str, value: Any) -> None:
    _GLOBAL_CACHE[key] = value


def get_cache(key: str, default: Any = None) -> Any:
    return _GLOBAL_CACHE.get(key, default)


def clear_cache() -> None:
    _GLOBAL_CACHE.clear()
