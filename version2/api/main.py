"""
CareerPivots FastAPI backend.

Exposes the resume-to-job-match pipeline as REST endpoints consumed by the
React frontend.  Intentionally avoids importing streamlit so this module can
run in a plain Python / uvicorn environment.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from functools import lru_cache
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── path: add version2/ so sibling packages resolve without the version2. prefix
_VERSION2_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _VERSION2_DIR not in sys.path:
    sys.path.insert(0, _VERSION2_DIR)

from core.models.embedding_model import load_embedding_provider
from core.similarity import compute_top_k
from core.supabase_client import get_supabase_client
from core.utils.logging import get_logger
from infra.config import load_settings
from services.experience_embedding_service import aggregate_experience_embeddings
from services.job_matching import normalize_title, prepare_job_matches
from services.match_explanation_service import MatchExplanationError, explain_match
from services.resume_extraction_service import extract_experiences
from services.stats_service import load_stats_for_display

_log = get_logger(__name__)

# ── startup: load config + embedding model once ───────────────────────────────
cfg = load_settings()
embedding_provider = load_embedding_provider(cfg.embeddings)

# ── data loaders (streamlit-free; process-level lru_cache) ───────────────────
_PAGE_SIZE = 1000


def _fetch_all_rows(table_name: str) -> List[dict]:
    supabase = get_supabase_client()
    rows, page = [], 0
    while True:
        start = page * _PAGE_SIZE
        resp = (
            supabase.table(table_name)
            .select("*")
            .range(start, start + _PAGE_SIZE - 1)
            .execute()
        )
        chunk = resp.data or []
        rows.extend(chunk)
        if len(chunk) < _PAGE_SIZE:
            break
        page += 1
    return rows


@lru_cache(maxsize=1)
def _load_embeddings() -> tuple[List[np.ndarray], List[dict]]:
    _log.info("Loading job embeddings from Supabase…")
    raw = _fetch_all_rows("jobhop_embeddings")
    vectors: List[np.ndarray] = []
    jobs: List[dict] = []
    for row in raw:
        try:
            emb = row["embedding"]
            if isinstance(emb, str):
                emb = json.loads(emb)
            arr = np.array(emb, dtype=float)
            if arr.ndim == 2:
                arr = arr.mean(axis=0)
            arr = arr.reshape(-1)
        except Exception as exc:
            _log.warning(
                "Skipping malformed embedding job_id=%s: %s", row.get("job_id"), exc
            )
            continue
        vectors.append(arr)
        title = row.get("title") or ""
        jobs.append(
            {
                "job_id": row.get("job_id"),
                "title": title,
                "normalized_title": normalize_title(title),
                "description": row.get("description"),
            }
        )
    _log.info("Loaded %d job embeddings.", len(vectors))
    return vectors, jobs


@lru_cache(maxsize=1)
def _load_stats() -> Dict[str, Any]:
    _log.info("Loading job stats from Supabase…")
    supabase = get_supabase_client()
    stats = load_stats_for_display(supabase)
    _log.info("Loaded stats for %d job titles.", len(stats))
    return stats


# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(title="CareerPivots API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── request / response schemas ────────────────────────────────────────────────
class MatchRequest(BaseModel):
    resume_text: str
    preferences: Optional[str] = ""
    exclusions: Optional[str] = ""
    match_count: int = 10


class TopTransition(BaseModel):
    jobTitle: str
    percentage: float


class Insights(BaseModel):
    percentOfDatabase: Optional[float] = None
    frequencyRank: Optional[int] = None
    averageTenure: Optional[float] = None
    medianTenure: Optional[float] = None
    topTransitions: List[TopTransition] = []


class JobMatch(BaseModel):
    id: str
    jobTitle: str
    jobDescription: str
    matchPercentage: float
    matchReason: str
    insights: Insights


# ── helpers ───────────────────────────────────────────────────────────────────
def _parse_transitions(raw: Any) -> List[TopTransition]:
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return []
    if not isinstance(raw, list):
        return []
    result: List[TopTransition] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = (
            item.get("next_job_title")
            or item.get("job_title")
            or item.get("jobTitle")
            or item.get("title")
            or ""
        )
        pct = float(
            item.get("percentage") or item.get("percent") or item.get("count") or 0.0
        )
        if title:
            result.append(TopTransition(jobTitle=title, percentage=pct))
    return result


# ── endpoints ─────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/match", response_model=List[JobMatch])
def match_jobs(req: MatchRequest) -> List[JobMatch]:
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text must not be empty")

    # 1. Extract structured experiences from resume text via Groq
    try:
        experiences = extract_experiences(req.resume_text, cfg.resume_extraction)
    except Exception as exc:
        _log.error("Experience extraction failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="Failed to extract experiences from resume"
        )

    if not experiences:
        raise HTTPException(
            status_code=422, detail="No work experiences found in the provided text"
        )

    # 2. Build aggregate resume embedding
    try:
        resume_vector: np.ndarray = aggregate_experience_embeddings(
            experiences, embedding_provider
        )
    except Exception as exc:
        _log.error("Embedding generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="Embedding generation failed")

    # 3. Load precomputed job data (process-cached after first request)
    job_vectors, jobs = _load_embeddings()
    stats_by_title = _load_stats()

    if not job_vectors:
        raise HTTPException(
            status_code=503, detail="Job embedding data is unavailable"
        )

    # 4. Cosine similarity search
    top_k = min(req.match_count, len(job_vectors))
    raw_matches = compute_top_k(resume_vector.tolist(), job_vectors, top_k=top_k)

    # 5. Join similarity results with job metadata and stats
    display_rows = prepare_job_matches(raw_matches, jobs, stats_by_title)

    # 6. Generate per-match explanations and shape final response
    result: List[JobMatch] = []
    for i, row in enumerate(display_rows):
        job_for_explain = {"description": row.get("description", "")}
        try:
            reason = explain_match(experiences, job_for_explain, cfg.resume_extraction)
        except MatchExplanationError as exc:
            _log.warning("Explanation skipped for '%s': %s", row.get("title"), exc)
            reason = (
                f"Your background aligns with the skills and responsibilities "
                f"of a {row.get('title', 'this role')}."
            )

        stats = row.get("stats", {})
        result.append(
            JobMatch(
                id=str(uuid.uuid4()),
                jobTitle=row.get("title", ""),
                jobDescription=row.get("description", ""),
                matchPercentage=round(row.get("similarity", 0.0), 1),
                matchReason=reason,
                insights=Insights(
                    percentOfDatabase=stats.get("percent_of_db"),
                    frequencyRank=stats.get("frequency_rank"),
                    averageTenure=stats.get("avg_tenure_years"),
                    medianTenure=stats.get("median_tenure_years"),
                    topTransitions=_parse_transitions(stats.get("top_transitions")),
                ),
            )
        )

    return result
