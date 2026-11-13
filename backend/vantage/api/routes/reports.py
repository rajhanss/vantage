"""Report export endpoints (JSON, Markdown, HTML)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from vantage.data.storage.database import get_db
from vantage.report.generator import (
    generate_html_report,
    generate_json_report,
    generate_markdown_report,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{run_id}")
async def get_report(run_id: str, format: str = Query("json", pattern="^(json|markdown|html)$")) -> Response:
    """Download security assessment report for a run in JSON, Markdown, or HTML format."""
    db = get_db()
    cached = db.get_report(run_id, format)
    if cached:
        if format == "html":
            return HTMLResponse(content=cached)
        elif format == "markdown":
            return PlainTextResponse(content=cached, media_type="text/markdown")
        else:
            return Response(content=cached, media_type="application/json")

    summary = db.get_run(run_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    if format == "html":
        content = generate_html_report(summary)
        db.save_report(run_id, "html", content)
        return HTMLResponse(content=content)
    elif format == "markdown":
        content = generate_markdown_report(summary)
        db.save_report(run_id, "markdown", content)
        return PlainTextResponse(content=content, media_type="text/markdown")
    else:
        content = generate_json_report(summary)
        db.save_report(run_id, "json", content)
        return Response(content=content, media_type="application/json")
