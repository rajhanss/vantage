"""Before-and-after defense comparison endpoint."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from vantage.data.storage.database import get_db
from vantage.models.domain import RunComparison
from vantage.scoring.calculator import compare_runs

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.get("", response_model=RunComparison)
@router.get("/", response_model=RunComparison, include_in_schema=False)
async def compare_two_runs(
    baseline_id: str = Query(..., description="Run ID of the baseline/vulnerable target run"),
    hardened_id: str = Query(..., description="Run ID of the hardened defense target run"),
) -> RunComparison:
    """Compare a baseline run against a hardened run to measure defense efficacy delta."""
    db = get_db()
    baseline = db.get_run(baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail=f"Baseline run '{baseline_id}' not found")

    hardened = db.get_run(hardened_id)
    if not hardened:
        raise HTTPException(status_code=404, detail=f"Hardened run '{hardened_id}' not found")

    return compare_runs(baseline, hardened)
