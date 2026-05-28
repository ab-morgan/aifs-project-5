"""
timing.py

Simple timing utilities for profiling steps in the prep pipeline
or runtime operations.

Usage:
    with time_block("embedding batch"):
        do_work()
"""

from __future__ import annotations

import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def time_block(label: str):
    """
    Context manager to measure execution time of a code block.

    Args:
        label (str): Description of the operation being timed.
    """
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        elapsed = end - start
        logger.info(f"[TIMER] {label}: {elapsed:.4f} seconds")
