"""Entity relationship graph endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Query
from vantage.data.storage.database import get_db
from vantage.intelligence.graph.builder import (
    build_entity_graph,
    compute_centralities,
    detect_communities,
    to_graph_data,
)
from vantage.models.domain import GraphData

router = APIRouter(prefix="/api/v1")


@router.get("/graph", response_model=GraphData)
async def get_graph(
    limit: int = Query(default=100, ge=10, le=300),
) -> GraphData:
    db = get_db()
    entities = db.list_entities(limit=limit)
    relationships = db.get_relationships(limit=1000)

    G = build_entity_graph(entities, relationships)
    centralities = compute_centralities(G)
    communities = detect_communities(G)

    return to_graph_data(G, centralities, communities)
