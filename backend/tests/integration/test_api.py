"""Integration tests — FastAPI TestClient against in-memory SQLite database."""
from __future__ import annotations

import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_db(tmp_path):
    """Provide an isolated SQLite database for each test."""
    from vantage.data.storage.database import Database
    db = Database(db_path=tmp_path / "test.db")
    return db


@pytest.fixture
def client(test_db):
    """Provide a TestClient backed by the isolated database."""
    import vantage.api.routes.ingest as ingest_module
    from vantage.data.storage.database import set_db

    # Reset the running flag between tests
    ingest_module._running = False
    set_db(test_db)

    from vantage.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c

    set_db(None)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_contains_status(self, client):
        resp = client.get("/health")
        assert resp.json()["status"] == "healthy"

    def test_stats_endpoint(self, client):
        resp = client.get("/api/v1/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "database" in data
        assert "entities" in data["database"]


class TestSignalsEndpoint:
    def test_empty_signals(self, client):
        resp = client.get("/api/v1/signals")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_signals_with_data(self, client, test_db):
        from vantage.models.domain import Entity, EntityType, Signal, SignalType

        entity = Entity(name="test/repo", entity_type=EntityType.REPOSITORY)
        test_db.upsert_entity(entity)

        signal = Signal(
            entity_id=entity.id,
            entity_name="test/repo",
            entity_type=EntityType.REPOSITORY,
            signal_type=SignalType.GROWTH_SURGE,
            z_score=3.5,
            velocity=100.0,
            acceleration=10.0,
            confidence=0.8,
            summary="Test signal",
        )
        test_db.upsert_signal(signal)

        resp = client.get("/api/v1/signals")
        assert resp.status_code == 200
        signals = resp.json()
        assert len(signals) == 1
        assert signals[0]["z_score"] == pytest.approx(3.5)

    def test_min_z_score_filter(self, client, test_db):
        resp = client.get("/api/v1/signals?min_z_score=10.0")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_limit_param(self, client):
        resp = client.get("/api/v1/signals?limit=5")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestTrendsEndpoint:
    def test_empty_trends(self, client):
        resp = client.get("/api/v1/trends")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_trend_detail_404(self, client):
        resp = client.get("/api/v1/trends/nonexistent-id")
        assert resp.status_code == 404

    def test_trend_detail_exists(self, client, test_db):
        from vantage.models.domain import Entity, EntityType, Observation, MetricType

        entity = Entity(name="transformers", entity_type=EntityType.PACKAGE)
        test_db.upsert_entity(entity)
        saved = test_db.get_entity_by_name("transformers", "package")

        for i in range(5):
            obs = Observation(
                entity_id=saved.id,
                source_id="pypi",
                metric_name=MetricType.DOWNLOADS.value,
                metric_value=float((i + 1) * 100_000),
                observed_at=datetime(2024, 1, i + 1, tzinfo=timezone.utc),
                collected_at=datetime(2024, 1, i + 1, tzinfo=timezone.utc),
            )
            test_db.insert_observation(obs)

        resp = client.get(f"/api/v1/trends/{saved.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["entity"]["name"] == "transformers"
        assert "momentum_score" in data
        assert "lifecycle_stage" in data


class TestGraphEndpoint:
    def test_empty_graph(self, client):
        resp = client.get("/api/v1/graph")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert "communities" in data

    def test_graph_with_entities(self, client, test_db):
        from vantage.models.domain import Entity, EntityType

        for i in range(5):
            test_db.upsert_entity(
                Entity(name=f"repo/{i}", entity_type=EntityType.REPOSITORY)
            )

        resp = client.get("/api/v1/graph")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 5


class TestInvestigateEndpoint:
    def test_investigate_missing_entity(self, client):
        resp = client.post("/api/v1/investigate", json={"entity_id": "does-not-exist"})
        assert resp.status_code == 404

    def test_investigate_existing_entity(self, client, test_db):
        from vantage.models.domain import Entity, EntityType

        entity = Entity(name="openai/gpt-4", entity_type=EntityType.REPOSITORY)
        test_db.upsert_entity(entity)
        saved = test_db.get_entity_by_name("openai/gpt-4", "repository")

        # No Groq key in test → rule-based fallback
        resp = client.post("/api/v1/investigate", json={"entity_id": saved.id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["entity_id"] == saved.id
        assert "title" in data
        assert "summary" in data
        assert isinstance(data["key_findings"], list)

    def test_investigations_list(self, client):
        resp = client.get("/api/v1/investigations")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestIngestEndpoint:
    def test_trigger_starts_ingestion(self, client):
        from unittest.mock import AsyncMock, patch
        with patch("vantage.data.pipelines.ingestion_runner.run_ingestion", new_callable=AsyncMock) as mock_ingest:
            mock_ingest.return_value = {"status": "ok"}
            resp = client.post("/api/v1/ingest/trigger")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] in ("started", "already_running")

    def test_status_endpoint(self, client):
        resp = client.get("/api/v1/ingest/status")
        assert resp.status_code == 200
        assert "running" in resp.json()


class TestRecommendationsEndpoint:
    def test_missing_entity(self, client):
        resp = client.get("/api/v1/recommendations?entity_id=invalid")
        assert resp.status_code == 404

    def test_recommendations_for_entity(self, client, test_db):
        from vantage.models.domain import Entity, EntityType

        entities = [
            Entity(name=f"pkg/{i}", entity_type=EntityType.PACKAGE)
            for i in range(5)
        ]
        for e in entities:
            test_db.upsert_entity(e)

        saved = test_db.get_entity_by_name("pkg/0", "package")
        resp = client.get(f"/api/v1/recommendations?entity_id={saved.id}&top_k=3")
        assert resp.status_code == 200
        recs = resp.json()
        assert isinstance(recs, list)
