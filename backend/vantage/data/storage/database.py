"""SQLite persistence layer for Vantage."""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from vantage.core.config import get_settings
from vantage.core.logging import get_logger
from vantage.models.domain import (
    Entity,
    EvidenceSource,
    InvestigationDossier,
    Observation,
    Signal,
)

log = get_logger(__name__)

_local = threading.local()


def _get_conn(db_path: Path) -> sqlite3.Connection:
    if not hasattr(_local, "conns"):
        _local.conns = {}
    key = str(db_path.resolve())
    conn = _local.conns.get(key)
    if conn is None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        _local.conns[key] = conn
    return conn


class Database:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_settings().db_path
        self._lock = threading.Lock()
        self._init_schema()

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        conn = _get_conn(self.db_path)
        with self._lock:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def _init_schema(self) -> None:
        with self._tx() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    primary_url TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    domain TEXT DEFAULT 'technology',
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_entities_name_type
                    ON entities(name, entity_type);

                CREATE TABLE IF NOT EXISTS observations (
                    id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL REFERENCES entities(id),
                    source_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    observed_at TEXT NOT NULL,
                    collected_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_obs_dedup
                    ON observations(entity_id, metric_name, source_id, date(observed_at));
                CREATE INDEX IF NOT EXISTS idx_obs_entity ON observations(entity_id);

                CREATE TABLE IF NOT EXISTS signals (
                    id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    entity_name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    z_score REAL NOT NULL,
                    velocity REAL NOT NULL,
                    acceleration REAL NOT NULL,
                    confidence REAL NOT NULL,
                    detected_at TEXT NOT NULL,
                    summary TEXT DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_signals_entity ON signals(entity_id);
                CREATE INDEX IF NOT EXISTS idx_signals_z ON signals(z_score DESC);

                CREATE TABLE IF NOT EXISTS investigations (
                    id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    entity_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    key_findings TEXT DEFAULT '[]',
                    evidence_sources TEXT DEFAULT '[]',
                    contradictions TEXT DEFAULT '[]',
                    confidence_score REAL DEFAULT 0.85,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_entity_id TEXT NOT NULL,
                    target_entity_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL DEFAULT 'co_occurs_with',
                    weight REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_rel_pair
                    ON relationships(source_entity_id, target_entity_id, relation_type);
            """)

    # --- Entity CRUD ---

    def upsert_entity(self, entity: Entity) -> Entity:
        with self._tx() as conn:
            conn.execute(
                """INSERT INTO entities
                   (id, name, entity_type, primary_url, description, domain, metadata, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(name, entity_type) DO UPDATE SET
                       primary_url=excluded.primary_url,
                       description=excluded.description,
                       metadata=excluded.metadata,
                       updated_at=excluded.updated_at""",
                (
                    entity.id,
                    entity.name,
                    entity.entity_type.value,
                    entity.primary_url,
                    entity.description,
                    entity.domain,
                    json.dumps(entity.metadata),
                    entity.created_at.isoformat(),
                    entity.updated_at.isoformat(),
                ),
            )
        return entity

    def get_entity(self, entity_id: str) -> Entity | None:
        with self._tx() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE id=?", (entity_id,)
            ).fetchone()
        return _row_to_entity(row) if row else None

    def get_entity_by_name(self, name: str, entity_type: str) -> Entity | None:
        with self._tx() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE name=? AND entity_type=?",
                (name, entity_type),
            ).fetchone()
        return _row_to_entity(row) if row else None

    def list_entities(self, limit: int = 200) -> list[Entity]:
        with self._tx() as conn:
            rows = conn.execute(
                "SELECT * FROM entities ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [_row_to_entity(r) for r in rows]

    # --- Observation CRUD ---

    def insert_observation(self, obs: Observation) -> bool:
        try:
            with self._tx() as conn:
                conn.execute(
                    """INSERT OR IGNORE INTO observations
                       (id, entity_id, source_id, metric_name, metric_value, observed_at, collected_at)
                       VALUES (?,?,?,?,?,?,?)""",
                    (
                        obs.id,
                        obs.entity_id,
                        obs.source_id,
                        obs.metric_name,
                        obs.metric_value,
                        obs.observed_at.isoformat(),
                        obs.collected_at.isoformat(),
                    ),
                )
            return True
        except Exception as e:
            log.warning("observation.insert_failed", error=str(e))
            return False

    def get_observations(
        self, entity_id: str, metric_name: str, limit: int = 90
    ) -> list[Observation]:
        with self._tx() as conn:
            rows = conn.execute(
                """SELECT * FROM observations
                   WHERE entity_id=? AND metric_name=?
                   ORDER BY observed_at ASC LIMIT ?""",
                (entity_id, metric_name, limit),
            ).fetchall()
        return [_row_to_observation(r) for r in rows]

    def get_all_observations(self, entity_id: str, limit: int = 200) -> list[Observation]:
        with self._tx() as conn:
            rows = conn.execute(
                "SELECT * FROM observations WHERE entity_id=? ORDER BY observed_at ASC LIMIT ?",
                (entity_id, limit),
            ).fetchall()
        return [_row_to_observation(r) for r in rows]

    # --- Signal CRUD ---

    def upsert_signal(self, signal: Signal) -> None:
        with self._tx() as conn:
            conn.execute(
                """INSERT INTO signals
                   (id, entity_id, entity_name, entity_type, signal_type,
                    z_score, velocity, acceleration, confidence, detected_at, summary)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                       z_score=excluded.z_score,
                       velocity=excluded.velocity,
                       acceleration=excluded.acceleration,
                       detected_at=excluded.detected_at,
                       summary=excluded.summary""",
                (
                    signal.id,
                    signal.entity_id,
                    signal.entity_name,
                    signal.entity_type.value,
                    signal.signal_type.value,
                    signal.z_score,
                    signal.velocity,
                    signal.acceleration,
                    signal.confidence,
                    signal.detected_at.isoformat(),
                    signal.summary,
                ),
            )

    def list_signals(self, limit: int = 50, min_z: float = 0.0) -> list[Signal]:
        with self._tx() as conn:
            rows = conn.execute(
                """SELECT * FROM signals WHERE z_score >= ?
                   ORDER BY z_score DESC, detected_at DESC LIMIT ?""",
                (min_z, limit),
            ).fetchall()
        return [_row_to_signal(r) for r in rows]

    def get_signals_for_entity(self, entity_id: str) -> list[Signal]:
        with self._tx() as conn:
            rows = conn.execute(
                "SELECT * FROM signals WHERE entity_id=? ORDER BY detected_at DESC LIMIT 10",
                (entity_id,),
            ).fetchall()
        return [_row_to_signal(r) for r in rows]

    # --- Investigation CRUD ---

    def save_investigation(self, dossier: InvestigationDossier) -> None:
        with self._tx() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO investigations
                   (id, entity_id, entity_name, title, summary, key_findings,
                    evidence_sources, contradictions, confidence_score, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    dossier.id,
                    dossier.entity_id,
                    dossier.entity_name,
                    dossier.title,
                    dossier.summary,
                    json.dumps(dossier.key_findings),
                    json.dumps([e.model_dump() for e in dossier.evidence_sources]),
                    json.dumps(dossier.contradictions),
                    dossier.confidence_score,
                    dossier.created_at.isoformat(),
                ),
            )

    def get_investigation(self, investigation_id: str) -> InvestigationDossier | None:
        with self._tx() as conn:
            row = conn.execute(
                "SELECT * FROM investigations WHERE id=?", (investigation_id,)
            ).fetchone()
        return _row_to_investigation(row) if row else None

    def list_investigations(self, limit: int = 20) -> list[InvestigationDossier]:
        with self._tx() as conn:
            rows = conn.execute(
                "SELECT * FROM investigations ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [_row_to_investigation(r) for r in rows]

    # --- Relationships ---

    def upsert_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str = "co_occurs_with",
        weight: float = 1.0,
    ) -> None:
        import uuid

        with self._tx() as conn:
            conn.execute(
                """INSERT INTO relationships
                   (id, source_entity_id, target_entity_id, relation_type, weight, created_at)
                   VALUES (?,?,?,?,?,?)
                   ON CONFLICT(source_entity_id, target_entity_id, relation_type)
                   DO UPDATE SET weight=weight+1""",
                (
                    str(uuid.uuid4()),
                    source_id,
                    target_id,
                    relation_type,
                    weight,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get_relationships(self, limit: int = 500) -> list[dict]:
        with self._tx() as conn:
            rows = conn.execute(
                """SELECT source_entity_id, target_entity_id, relation_type, weight
                   FROM relationships LIMIT ?""",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        with self._tx() as conn:
            stats = {}
            for table in ("entities", "observations", "signals", "investigations"):
                row = conn.execute(f"SELECT COUNT(*) as n FROM {table}").fetchone()
                stats[table] = row["n"] if row else 0
        return stats


# ---- Row converters ----


def _row_to_entity(row: sqlite3.Row) -> Entity:
    from vantage.models.domain import EntityType

    d = dict(row)
    d["metadata"] = json.loads(d.get("metadata") or "{}")
    d["entity_type"] = EntityType(d["entity_type"])
    d["created_at"] = datetime.fromisoformat(d["created_at"])
    d["updated_at"] = datetime.fromisoformat(d["updated_at"])
    return Entity(**d)


def _row_to_observation(row: sqlite3.Row) -> Observation:
    d = dict(row)
    d["observed_at"] = datetime.fromisoformat(d["observed_at"])
    d["collected_at"] = datetime.fromisoformat(d["collected_at"])
    return Observation(**d)


def _row_to_signal(row: sqlite3.Row) -> Signal:
    from vantage.models.domain import EntityType, SignalType

    d = dict(row)
    d["entity_type"] = EntityType(d["entity_type"])
    d["signal_type"] = SignalType(d["signal_type"])
    d["detected_at"] = datetime.fromisoformat(d["detected_at"])
    return Signal(**d)


def _row_to_investigation(row: sqlite3.Row) -> InvestigationDossier:
    d = dict(row)
    d["key_findings"] = json.loads(d.get("key_findings") or "[]")
    d["evidence_sources"] = [
        EvidenceSource(**e)
        for e in json.loads(d.get("evidence_sources") or "[]")
    ]
    d["contradictions"] = json.loads(d.get("contradictions") or "[]")
    d["created_at"] = datetime.fromisoformat(d["created_at"])
    return InvestigationDossier(**d)


_db_instance: Database | None = None


def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def set_db(db: Database | None) -> None:
    global _db_instance
    _db_instance = db
