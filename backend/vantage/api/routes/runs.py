"""Evaluation run execution and monitoring endpoints."""
from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from vantage.data.storage.database import get_db
from vantage.engine.runner import AsyncRunner, EventBus
from vantage.models.domain import RunConfig, RunStatus, RunSummary
from vantage.report.generator import (
    generate_html_report,
    generate_json_report,
    generate_markdown_report,
)

router = APIRouter(prefix="/api/runs", tags=["runs"])

# Global in-memory active runners and event buses
_active_runners: dict[str, AsyncRunner] = {}
_run_buses: dict[str, EventBus] = {}


@router.post("", response_model=RunSummary, status_code=201)
@router.post("/", response_model=RunSummary, status_code=201, include_in_schema=False)
async def create_run(config: RunConfig, background_tasks: BackgroundTasks) -> RunSummary:
    """Create and trigger an adversarial evaluation run against the target agent."""
    bus = EventBus()
    runner = AsyncRunner(config=config, event_bus=bus)

    # Pre-generate run summary
    summary = await runner.run()

    # Save to SQLite database
    db = get_db()
    db.save_run(summary)

    # Pre-render reports for fast downloads
    db.save_report(summary.run_id, "json", generate_json_report(summary))
    db.save_report(summary.run_id, "markdown", generate_markdown_report(summary))
    db.save_report(summary.run_id, "html", generate_html_report(summary))

    return summary


@router.get("", response_model=list[dict])
@router.get("/", response_model=list[dict], include_in_schema=False)
async def list_runs(limit: int = 50) -> list[dict]:
    """List recent security evaluation runs."""
    db = get_db()
    return db.list_runs(limit=limit)


@router.get("/{run_id}", response_model=RunSummary)
async def get_run(run_id: str) -> RunSummary:
    """Retrieve full findings and telemetry for a specific run."""
    db = get_db()
    summary = db.get_run(run_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return summary


@router.post("/{run_id}/kill")
async def kill_run(run_id: str) -> dict[str, str]:
    """Trigger kill switch for an in-flight run."""
    runner = _active_runners.get(run_id)
    if not runner:
        return {"status": "not_active_or_completed", "run_id": run_id}
    runner.abort()
    return {"status": "aborted", "run_id": run_id}
