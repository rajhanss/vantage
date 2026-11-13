"""Vantage FastAPI application entry point.

Adversarial testing and security assessment framework for autonomous AI agents.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vantage.api.routes import compare, health, reports, runs, scenarios
from vantage.core.config import get_settings
from vantage.core.logging import configure_logging
from vantage.data.storage.database import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    # Pre-initialise SQLite database schema
    get_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Vantage — Agent Security Assessment Framework",
        description=(
            "Adversarial testing and security assessment framework for autonomous AI agents. "
            "Evaluates agent resilience against the OWASP Top 10 for Agentic Applications (ASI01-ASI10) "
            "using reproducible trials, deterministic canary oracles, and statistical Wilson score intervals."
        ),
        version=settings.version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(health.router)
    app.include_router(scenarios.router)
    app.include_router(runs.router)
    app.include_router(reports.router)
    app.include_router(compare.router)

    # Static UI — serve React frontend dashboard if present
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            # API requests should have already been handled above
            if full_path.startswith("api/") or full_path == "health":
                return FileResponse(static_dir / "index.html")
            file_candidate = static_dir / full_path
            if file_candidate.is_file():
                return FileResponse(file_candidate)
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()
