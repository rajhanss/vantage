"""Health check endpoint for Vantage."""
from __future__ import annotations

from fastapi import APIRouter
from vantage.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "vantage",
        "description": "Adversarial testing & security assessment framework for autonomous AI agents",
        "version": settings.version,
    }
