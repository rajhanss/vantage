"""Integration tests for Vantage FastAPI endpoints."""
from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from vantage.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "vantage"


def test_list_scenarios_endpoint(client: TestClient):
    resp = client.get("/api/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert len(scenarios) >= 10
    assert any(s["category"] == "ASI01" for s in scenarios)


def test_get_scenario_by_id(client: TestClient):
    resp = client.get("/api/scenarios/asi01-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "asi01-01"
    assert data["category"] == "ASI01"


def test_create_and_fetch_run(client: TestClient):
    payload = {
        "target_spec": {
            "name": "Integration-Testbed",
            "type": "in_process",
            "mode": "vulnerable",
        },
        "selected_categories": ["ASI01"],
        "trials_per_scenario": 1,
        "seed": 42,
    }
    resp = client.post("/api/runs", json=payload)
    assert resp.status_code == 201
    run_data = resp.json()
    run_id = run_data["run_id"]
    assert run_data["status"] == "completed"

    # Fetch run
    get_resp = client.get(f"/api/runs/{run_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["run_id"] == run_id

    # Fetch report in JSON
    json_rep = client.get(f"/api/reports/{run_id}?format=json")
    assert json_rep.status_code == 200

    # Fetch report in Markdown
    md_rep = client.get(f"/api/reports/{run_id}?format=markdown")
    assert md_rep.status_code == 200
    assert "# Vantage Security Assessment Report" in md_rep.text

    # Fetch report in HTML
    html_rep = client.get(f"/api/reports/{run_id}?format=html")
    assert html_rep.status_code == 200
    assert "<!DOCTYPE html>" in html_rep.text
