"""On-demand ingestion trigger endpoint."""
from __future__ import annotations

import asyncio
from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/api/v1")

_running = False


@router.post("/ingest/trigger")
async def trigger_ingestion(background_tasks: BackgroundTasks) -> dict:
    global _running
    if _running:
        return {"status": "already_running", "message": "Ingestion already in progress"}

    async def run():
        global _running
        _running = True
        try:
            from vantage.data.pipelines.ingestion_runner import run_ingestion
            result = await run_ingestion()
            return result
        finally:
            _running = False

    background_tasks.add_task(run)
    return {"status": "started", "message": "Ingestion triggered in background"}


@router.get("/ingest/status")
async def ingest_status() -> dict:
    return {"running": _running}
