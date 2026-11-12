"""Trend discovery and detail endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from vantage.data.storage.database import get_db
from vantage.intelligence.forecasting.engine import forecast_entity
from vantage.intelligence.signals.detector import (
    compute_acceleration,
    compute_rolling_z_score,
    compute_velocity,
)
from vantage.intelligence.temporal.modeler import (
    classify_lifecycle_stage,
    compute_momentum_score,
)
from vantage.models.domain import Entity, TrendDetail, MetricType

router = APIRouter(prefix="/api/v1")

_METRIC_PRIORITY = [
    MetricType.STARS.value,
    MetricType.DOWNLOADS.value,
    MetricType.ENGAGEMENT.value,
    MetricType.FORKS.value,
    MetricType.MENTIONS.value,
    MetricType.COMMENT_COUNT.value,
]


def _build_trend_detail(entity: Entity, db) -> TrendDetail:
    # Pick primary metric
    primary_obs = []
    for metric in _METRIC_PRIORITY:
        obs = db.get_observations(entity.id, metric, limit=90)
        if obs:
            primary_obs = obs
            break

    all_obs = db.get_all_observations(entity.id, limit=200)
    values = [o.metric_value for o in primary_obs]

    velocity = compute_velocity(values) if len(values) >= 2 else 0.0
    acceleration = compute_acceleration(values) if len(values) >= 3 else 0.0
    z_score = compute_rolling_z_score(values) if len(values) >= 3 else 0.0
    momentum = compute_momentum_score(velocity, z_score, acceleration)
    stage = classify_lifecycle_stage(velocity, acceleration, z_score)

    forecast = forecast_entity(primary_obs, horizon_days=30) if len(primary_obs) >= 2 else None

    return TrendDetail(
        entity=entity,
        current_velocity=round(velocity, 4),
        acceleration=round(acceleration, 4),
        momentum_score=round(momentum, 4),
        lifecycle_stage=stage,
        observations=all_obs[:100],
        forecast=forecast,
        related_entities=[],
    )


@router.get("/trends", response_model=list[TrendDetail])
async def list_trends(
    limit: int = Query(default=20, ge=1, le=100),
    entity_type: str = Query(default=""),
) -> list[TrendDetail]:
    db = get_db()
    entities = db.list_entities(limit=200)
    if entity_type:
        entities = [e for e in entities if e.entity_type.value == entity_type]

    results = []
    for entity in entities[:limit]:
        results.append(_build_trend_detail(entity, db))

    results.sort(key=lambda t: t.momentum_score, reverse=True)
    return results


@router.get("/trends/{entity_id}", response_model=TrendDetail)
async def get_trend(entity_id: str) -> TrendDetail:
    db = get_db()
    entity = db.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id!r} not found")
    return _build_trend_detail(entity, db)
