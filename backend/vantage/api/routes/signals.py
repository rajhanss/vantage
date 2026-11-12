"""Signal detection endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query
from vantage.data.storage.database import get_db
from vantage.models.domain import Signal

router = APIRouter(prefix="/api/v1")


@router.get("/signals", response_model=list[Signal])
async def list_signals(
    limit: int = Query(default=50, ge=1, le=200),
    min_z_score: float = Query(default=0.0, ge=0.0),
) -> list[Signal]:
    db = get_db()
    return db.list_signals(limit=limit, min_z=min_z_score)
