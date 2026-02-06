"""
prep_runner.py

The orchestrator for the PREP pipeline.

This script:
1. Runs verify_data() to ensure the environment is ready.
2. Generates embeddings if missing.
3. Computes stats if missing or if embeddings were regenerated.
4. Produces a final summary and logs all steps.

This file should be run BEFORE launching the Streamlit app.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Any

from prep.verify_data import verify_data
from prep.compute_embeddings import compute_embeddings
from prep.compute_stats import compute_stats

logger = logging.getLogger(__name__)


def run_prep() -> Dict[str, Any]:
    """
    Main entrypoint for the full prep pipeline.

    Returns:
        dict: Summary of the entire prep process.
    """
    logger.info("=== PREP PIPELINE STARTED ===")

    # Step 1 — Verify environment
    report = verify_data()

    if not report.get("tables_ok") or not report.get("schema_ok"):
        logger.error("Prep aborted: database tables or schema are not ready.")
        return {
            "status": "failed",
            "reason": "Database tables or schema not ready",
            "verify_report": report,
        }

    embeddings_needed = report.get("missing_embeddings", True)
    stats_needed = report.get("missing_stats", True)

    embeddings_summary = None
    stats_summary = None

    # Step 2 — Generate embeddings if needed
    if embeddings_needed:
        logger.info("Embeddings missing — generating embeddings...")
        embeddings_summary = compute_embeddings()
    else:
        logger.info("Embeddings already exist — skipping embedding generation.")

    # Step 3 — Compute stats if needed OR if embeddings were regenerated
    if stats_needed or embeddings_needed:
        logger.info("Stats missing or embeddings updated — computing stats...")
        stats_summary = compute_stats()
    else:
        logger.info("Stats already exist — skipping stats computation.")

    final_summary = {
        "status": "success",
        "verify_report": report,
        "embeddings_generated": embeddings_needed,
        "stats_generated": stats_needed or embeddings_needed,
        "embeddings_summary": embeddings_summary,
        "stats_summary": stats_summary,
    }

    logger.info("=== PREP PIPELINE COMPLETED ===")
    logger.info(json.dumps(final_summary, indent=2))

    return final_summary


if __name__ == "__main__":
    logging.basicConfig(
        filename="logs/prep.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = run_prep()
    print(json.dumps(result, indent=2))
