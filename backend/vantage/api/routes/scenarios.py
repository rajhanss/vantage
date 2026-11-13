"""Scenario management and inspection endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from vantage.models.domain import OWASP_CATEGORY_META, OwaspCategory, Scenario
from vantage.scenarios.loader import load_all_scenarios

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


@router.get("", response_model=list[Scenario])
@router.get("/", response_model=list[Scenario], include_in_schema=False)
async def list_scenarios(category: OwaspCategory | None = None) -> list[Scenario]:
    """List all available attack scenarios across OWASP ASI01-ASI10."""
    all_scenarios = load_all_scenarios()
    if category:
        return [s for s in all_scenarios if s.category == category]
    return all_scenarios


@router.get("/categories")
async def list_categories() -> dict[str, dict[str, str]]:
    """Return OWASP Top 10 for Agentic Applications categories and titles."""
    return {k.value: v for k, v in OWASP_CATEGORY_META.items()}


@router.get("/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str) -> Scenario:
    """Retrieve details for a single scenario."""
    for s in load_all_scenarios():
        if s.id == scenario_id:
            return s
    raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
