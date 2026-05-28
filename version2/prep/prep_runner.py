"""
prep_runner.py

Orchestrates the full prep pipeline:

  1. verify_data   — check Supabase connectivity, tables, and model config
  2. compute_embeddings — embed all jobs in jobhop_raw → jobhop_embeddings
  3. compute_stats      — compute per-title stats → jobhop_stats

Each step is skipped if the data already exists (idempotent).
Pass --force to recompute everything from scratch.

Usage:
    python -m prep.prep_runner           # skip steps where data exists
    python -m prep.prep_runner --force   # recompute everything
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure version2/ is on the path when run as a module
_V2_ROOT = Path(__file__).resolve().parents[1]
if str(_V2_ROOT) not in sys.path:
    sys.path.insert(0, str(_V2_ROOT))

from core.utils.logging import configure_logging, get_logger
configure_logging()
logger = get_logger(__name__)

from prep.verify_data import verify_data
from prep.compute_embeddings import compute_embeddings
from prep.compute_stats import compute_stats
from infra.config import load_settings


def run_prep(force: bool = False) -> Dict[str, Any]:
    """
    Run the full prep pipeline.

    Behaviour is controlled by the [prep] section in settings.<env>.toml:
      - dev:  small batches, verbose logging, skip_if_exists=true
      - prod: full batches, errors-only logging, skip_if_exists=true

    Args:
        force: Recompute embeddings and stats even if they already exist
               (overrides skip_if_exists from config).

    Returns:
        Summary dict describing what was done.
    """
    config = load_settings()
    prep_cfg = config.prep
    env = config.app_env.env

    logger.info("=== PREP PIPELINE STARTED (env=%s, force=%s) ===", env, force)
    print(f"\n  CareerPivots prep pipeline [{env}] (force={force})")
    print(f"  batch_size={prep_cfg.batch_size}  skip_if_exists={prep_cfg.skip_if_exists}  source={prep_cfg.source_table}\n")

    # ── Step 1: Verify ────────────────────────────────────────────────────
    print("  [1/3] Verifying environment...")
    report = verify_data()

    if not report.get("tables_ok"):
        msg = "Database tables are not ready. Run the SQL in version2/infra/table.sql first."
        logger.error("Prep aborted: %s", msg)
        print(f"\n  ERROR: {msg}\n")
        return {"status": "failed", "reason": msg, "verify_report": report}

    if not report.get("model_ready"):
        msg = "Embedding model config is invalid. Check [embeddings] in settings.toml."
        logger.error("Prep aborted: %s", msg)
        print(f"\n  ERROR: {msg}\n")
        return {"status": "failed", "reason": msg, "verify_report": report}

    embeddings_needed = force or (prep_cfg.skip_if_exists is False) or report.get("missing_embeddings", True)
    stats_needed      = force or (prep_cfg.skip_if_exists is False) or report.get("missing_stats", True)

    # ── Step 2: Embeddings ────────────────────────────────────────────────
    embeddings_summary = None
    if embeddings_needed:
        print("  [2/3] Computing embeddings...")
        embeddings_summary = compute_embeddings(force=force)
        if embeddings_summary.get("status") == "no_jobs":
            print("  WARNING: No jobs found in jobhop_raw. Load job data first.")
        else:
            n = embeddings_summary.get("processed", 0)
            s = embeddings_summary.get("skipped", 0)
            print(f"  [2/3] Done — {n} embedded, {s} skipped.")
        # If embeddings were (re)computed, always recompute stats too
        stats_needed = True
    else:
        print("  [2/3] Embeddings already exist — skipping.")

    # ── Step 3: Stats ─────────────────────────────────────────────────────
    stats_summary = None
    if stats_needed:
        print("  [3/3] Computing statistics...")
        stats_summary = compute_stats()
        n = stats_summary.get("titles_processed", 0)
        print(f"  [3/3] Done — {n} job titles processed.")
    else:
        print("  [3/3] Stats already exist — skipping.")

    final = {
        "status": "success",
        "verify_report": report,
        "embeddings_generated": embeddings_needed,
        "stats_generated": stats_needed,
        "embeddings_summary": embeddings_summary,
        "stats_summary": stats_summary,
    }

    logger.info("=== PREP PIPELINE COMPLETED ===\n%s", json.dumps(final, indent=2, default=str))
    print("\n  Prep pipeline complete.\n")
    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CareerPivots prep pipeline")
    parser.add_argument("--force", action="store_true",
                        help="Recompute embeddings and stats even if they already exist")
    args = parser.parse_args()
    result = run_prep(force=args.force)
    print(json.dumps(result, indent=2, default=str))
