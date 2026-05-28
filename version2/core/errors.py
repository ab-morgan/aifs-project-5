"""
errors.py

Custom exception classes for version2.
"""


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""


class SupabaseError(Exception):
    """Raised when Supabase operations fail."""


class DataValidationError(Exception):
    """Raised when input data is malformed or incomplete."""
