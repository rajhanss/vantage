"""Investigation dossier endpoints."""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from vantage.data.storage.database import get_db
from vantage.intelligence.agents.orchestrator import investigate
from vantage.models.domain import InvestigationDossier

router = APIRouter(prefix="/api/v1")


class InvestigateRequest(BaseModel):
    entity_id: str


@router.post("/investigate", response_model=InvestigationDossier)
async def start_investigation(
    body: InvestigateRequest,
    background_tasks: BackgroundTasks,
) -> InvestigationDossier:
    db = get_db()
    entity = db.get_entity(body.entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {body.entity_id!r} not found")

    # Build observations summary
    obs = db.get_all_observations(entity.id, limit=50)
    if obs:
        latest = obs[-1]
        obs_summary = (
            f"{len(obs)} observations. Latest: {latest.metric_name}={latest.metric_value:.1f} "
            f"at {latest.observed_at.date()}"
        )
    else:
        obs_summary = "No observations collected yet."

    signals = db.get_signals_for_entity(entity.id)
    signal = signals[0] if signals else None

    dossier = await investigate(entity, signal, obs_summary)
    db.save_investigation(dossier)
    return dossier


@router.get("/investigations/{investigation_id}", response_model=InvestigationDossier)
async def get_investigation(investigation_id: str) -> InvestigationDossier:
    db = get_db()
    dossier = db.get_investigation(investigation_id)
    if not dossier:
        raise HTTPException(
            status_code=404,
            detail=f"Investigation {investigation_id!r} not found",
        )
    return dossier


@router.get("/investigations", response_model=list[InvestigationDossier])
async def list_investigations(limit: int = 20) -> list[InvestigationDossier]:
    db = get_db()
    return db.list_investigations(limit=limit)
