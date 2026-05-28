"""
verify_data.py

Validates that the environment, configuration, and Supabase database are
ready for the prep pipeline to run.

Checks:
- Supabase connectivity
- Required tables exist
- Embeddings presence (are there rows in jobhop_embeddings?)
- Stats presence (are there rows in jobhop_stats?)
- Embedding model configuration is valid

Returns a VerifyReport dict consumed by prep_runner.py.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any

from infra.config import load_settings
from core.supabase_client import get_supabase_client
from core.utils.logging import get_logger

logger = get_logger(__name__)

REQUIRED_TABLES = ["jobhop_raw", "jobhop_embeddings", "jobhop_stats"]


@dataclass
class VerifyReport:
    tables_ok: bool
    missing_embeddings: bool   # True  → embeddings need to be computed
    missing_stats: bool        # True  → stats need to be computed
    model: str
    model_ready: bool
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────

def _check_supabase_connection(supabase) -> bool:
    try:
        supabase.table("jobhop_raw").select("id").limit(1).execute()
        return True
    except Exception as e:
        logger.error("Supabase connection check failed: %s", e)
        return False


def _check_required_tables(supabase) -> Dict[str, bool]:
    results: Dict[str, bool] = {}
    for table in REQUIRED_TABLES:
        try:
            supabase.table(table).select("id").limit(1).execute()
            results[table] = True
        except Exception as e:
            logger.error("Table check failed for '%s': %s", table, e)
            results[table] = False
    return results


def _has_rows(supabase, table: str) -> bool:
    """Return True if the table contains at least one row."""
    try:
        resp = supabase.table(table).select("id").limit(1).execute()
        data = getattr(resp, "data", None) or []
        return len(data) > 0
    except Exception as e:
        logger.warning("Could not check row presence in '%s': %s", table, e)
        return False   # conservative: treat as empty so prep runs


def _validate_model_config(config) -> tuple[str, bool, Dict[str, Any]]:
    details: Dict[str, Any] = {}
    try:
        provider = config.embeddings.provider
        model_name = config.embeddings.model_name
        if not provider or not model_name:
            raise ValueError("provider or model_name is empty")
        model_key = f"{provider}/{model_name}"
        details.update({"provider": provider, "model_name": model_name})
        return model_key, True, details
    except Exception as e:
        details["error"] = str(e)
        return "", False, details


# ─────────────────────────────────────────────────────────────────────────────

def verify_data() -> Dict[str, Any]:
    """
    Main entrypoint for data verification.
    Returns a dict describing the state of the environment.
    """
    logger.info("Starting verify_data step...")

    config = load_settings()
    supabase = get_supabase_client()

    # 1. Connectivity
    if not _check_supabase_connection(supabase):
        report = VerifyReport(
            tables_ok=False, missing_embeddings=True, missing_stats=True,
            model="", model_ready=False,
            details={"error": "Supabase connection failed"},
        )
        logger.error("verify_data failed: Supabase connection failed")
        return report.to_dict()

    # 2. Tables
    table_results = _check_required_tables(supabase)
    tables_ok = all(table_results.values())

    # 3. Data presence — missing = needs to be (re)computed
    missing_embeddings = not _has_rows(supabase, "jobhop_embeddings")
    missing_stats      = not _has_rows(supabase, "jobhop_stats")

    # 4. Model config
    model_key, model_ready, model_details = _validate_model_config(config)

    report = VerifyReport(
        tables_ok=tables_ok,
        missing_embeddings=missing_embeddings,
        missing_stats=missing_stats,
        model=model_key,
        model_ready=model_ready,
        details={"tables": table_results, "model": model_details},
    )

    logger.info("verify_data report: %s", json.dumps(report.to_dict(), indent=2))
    return report.to_dict()
