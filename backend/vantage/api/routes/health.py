"""Health and stats endpoints."""
from __future__ import annotations

from fastapi import APIRouter
from vantage.core.config import get_settings
from vantage.data.storage.database import get_db

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "version": get_settings().version,
        "environment": get_settings().environment,
    }


@router.get("/api/v1/stats")
async def stats() -> dict:
    db = get_db()
    counts = db.get_stats()
    settings = get_settings()
    return {
        "version": settings.version,
        "environment": settings.environment,
        "database": counts,
        "adapters": ["github", "huggingface", "arxiv", "hackernews", "pypi"],
    }
