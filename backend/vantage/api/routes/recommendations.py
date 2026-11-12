"""Recommendation endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from vantage.data.storage.database import get_db
from vantage.intelligence.ranking.recommender import recommend_similar
from vantage.models.domain import Observation, Recommendation

router = APIRouter(prefix="/api/v1")


@router.get("/recommendations", response_model=list[Recommendation])
async def get_recommendations(
    entity_id: str = Query(..., description="Source entity ID to find similar entities for"),
    top_k: int = Query(default=10, ge=1, le=50),
) -> list[Recommendation]:
    db = get_db()
    entity = db.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id!r} not found")

    all_entities = db.list_entities(limit=500)

    # Build observation map (only primary metric per entity for efficiency)
    observations_map: dict[str, list[Observation]] = {}
    for e in all_entities:
        observations_map[e.id] = db.get_all_observations(e.id, limit=20)

    return recommend_similar(entity_id, all_entities, observations_map, top_k=top_k)
