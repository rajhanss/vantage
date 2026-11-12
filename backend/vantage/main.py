"""Vantage FastAPI application entry point."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vantage.api.routes import graph, health, ingest, investigate, recommendations, signals, trends
from vantage.core.config import get_settings
from vantage.core.logging import configure_logging
from vantage.data.storage.database import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    # Pre-initialise database
    get_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Vantage Intelligence API",
        description=(
            "Multimodal Temporal Intelligence and Discovery Platform. "
            "Collects signals from across the developer ecosystem and surfaces emerging trends."
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
    app.include_router(signals.router)
    app.include_router(trends.router)
    app.include_router(graph.router)
    app.include_router(investigate.router)
    app.include_router(recommendations.router)
    app.include_router(ingest.router)

    # Serve React frontend from static directory (populated during Docker build)
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            index = static_dir / "index.html"
            return FileResponse(str(index))

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    port = int(os.getenv("PORT", str(settings.port)))
    uvicorn.run("vantage.main:app", host=settings.host, port=port, reload=settings.debug)
