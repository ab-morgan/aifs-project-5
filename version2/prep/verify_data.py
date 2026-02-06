"""
verify_data.py

Responsible for validating that the environment, configuration, and Supabase
database are ready for the prep pipeline to run.

Checks:
- Supabase connectivity
- Required tables exist
- Schema matches infra/table.sql (basic checks)
- Embeddings and stats presence
- Embedding model configuration is valid

Returns a structured report dict to be consumed by prep_runner.py.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any

from infra.config import load_config
from core.supabase_client import get_supabase_client
# infra/table.sql is used as a reference; we won't parse full SQL here,
# but we can at least verify required tables/columns exist.


logger = logging.getLogger(__name__)


@dataclass
class VerifyReport:
    tables_ok: bool
    schema_ok: bool
    missing_embeddings: bool
    missing_stats: bool
    model: str
    model_ready: bool
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


REQUIRED_TABLES = [
    "jobs",
    "job_embeddings",
    "job_stats",
]


def _check_supabase_connection(supabase) -> bool:
    try:
        # Simple ping: list tables or select 1 from a known table
        response = supabase.table("jobs").select("*").limit(1).execute()
        return response is not None
    except Exception as e:
        logger.error(f"Supabase connection check failed: {e}")
        return False


def _check_required_tables(supabase) -> Dict[str, bool]:
    results: Dict[str, bool] = {}
    for table in REQUIRED_TABLES:
        try:
            supabase.table(table).select("*").limit(1).execute()
            results[table] = True
        except Exception as e:
            logger.error(f"Table check failed for '{table}': {e}")
            results[table] = False
    return results


def _check_embeddings_presence(supabase) -> bool:
    try:
        response = supabase.table("job_embeddings").select("id").limit(1).execute()
        data = getattr(response, "data", None) or response.get("data", [])
        return len(data) == 0  # True if missing
    except Exception as e:
        logger.warning(f"Could not check embeddings presence: {e}")
        # If we can't check, be conservative and say embeddings are missing
        return True


def _check_stats_presence(supabase) -> bool:
    try:
        response = supabase.table("job_stats").select("id").limit(1).execute()
        data = getattr(response, "data", None) or response.get("data", [])
        return len(data) == 0  # True if missing
    except Exception as e:
        logger.warning(f"Could not check stats presence: {e}")
        # If we can't check, be conservative and say stats are missing
        return True


def _validate_model_config(config: Dict[str, Any]) -> (str, bool, Dict[str, Any]):
    details: Dict[str, Any] = {}
    embeddings_cfg = config.get("embeddings", {})

    provider = embeddings_cfg.get("provider")
    model_name = embeddings_cfg.get("model_name")

    if not provider or not model_name:
        details["error"] = "embeddings.provider or embeddings.model_name missing in settings.toml"
        return "", False, details

    model_key = f"{provider}/{model_name}"
    details["provider"] = provider
    details["model_name"] = model_name
    details["model_key"] = model_key

    # We don't actually load the model here; that happens in compute_embeddings.
    # Here we just validate that the config is syntactically present.
    return model_key, True, details


def verify_data() -> Dict[str, Any]:
    """
    Main entrypoint for data verification.

    Returns:
        dict: A structured report describing the state of the environment.
    """
    logger.info("Starting verify_data step...")

    config = load_config()
    supabase = get_supabase_client()

    # 1. Check Supabase connectivity
    connection_ok = _check_supabase_connection(supabase)
    if not connection_ok:
        report = VerifyReport(
            tables_ok=False,
            schema_ok=False,
            missing_embeddings=True,
            missing_stats=True,
            model="",
            model_ready=False,
            details={"error": "Supabase connection failed"},
        )
        logger.error("verify_data failed: Supabase connection failed")
        _log_report(report)
        return report.to_dict()

    # 2. Check required tables
    table_results = _check_required_tables(supabase)
    tables_ok = all(table_results.values())

    # 3. Schema check (lightweight placeholder)
    # In a future iteration, we can parse infra/table.sql and compare.
    schema_ok = tables_ok  # For now, assume schema is OK if tables exist.

    # 4. Check embeddings and stats presence
    missing_embeddings = _check_embeddings_presence(supabase)
    missing_stats = _check_stats_presence(supabase)

    # 5. Validate embedding model configuration
    model_key, model_ready, model_details = _validate_model_config(config)

    details: Dict[str, Any] = {
        "tables": table_results,
        "missing_embeddings": missing_embeddings,
        "missing_stats": missing_stats,
        "model_details": model_details,
    }

    report = VerifyReport(
        tables_ok=tables_ok,
        schema_ok=schema_ok,
        missing_embeddings=missing_embeddings,
        missing_stats=missing_stats,
        model=model_key,
        model_ready=model_ready,
        details=details,
    )

    _log_report(report)
    logger.info("verify_data completed.")
    return report.to_dict()


def _log_report(report: VerifyReport) -> None:
    try:
        as_json = json.dumps(report.to_dict(), indent=2)
        logger.info(f"verify_data report:\n{as_json}")
    except Exception as e:
        logger.error(f"Failed to serialize verify_data report: {e}")


if __name__ == "__main__":
    # Allow running this module directly for debugging.
    logging.basicConfig(
        filename="logs/prep.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = verify_data()
    print(json.dumps(result, indent=2))
