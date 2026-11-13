"""SQLite repository for Vantage runs, findings, and reports."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import threading
from contextlib import contextmanager
from typing import Generator

from vantage.core.config import get_settings
from vantage.core.logging import get_logger
from vantage.models.domain import RunSummary

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
    """Thread-safe SQLite repository with WAL mode."""

    def __init__(self, db_path: Path | None = None) -> None:
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
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    target_name TEXT NOT NULL,
                    target_mode TEXT NOT NULL,
                    status TEXT NOT NULL,
                    overall_asr REAL NOT NULL,
                    wilson_lower REAL NOT NULL,
                    wilson_upper REAL NOT NULL,
                    risk_grade TEXT NOT NULL,
                    total_scenarios INTEGER NOT NULL,
                    total_trials INTEGER NOT NULL,
                    successful_attacks INTEGER NOT NULL,
                    duration_ms REAL NOT NULL,
                    summary_json TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS reports (
                    run_id TEXT NOT NULL,
                    format TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (run_id, format),
                    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
                CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at DESC);
                """
            )

    def save_run(self, summary: RunSummary) -> None:
        summary_json = summary.model_dump_json()
        with self._tx() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id, target_name, target_mode, status, overall_asr,
                    wilson_lower, wilson_upper, risk_grade, total_scenarios,
                    total_trials, successful_attacks, duration_ms, summary_json,
                    started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.run_id,
                    summary.target_name,
                    summary.target_mode,
                    summary.status.value,
                    summary.overall_asr,
                    summary.wilson_lower,
                    summary.wilson_upper,
                    summary.risk_grade.value,
                    summary.total_scenarios,
                    summary.total_trials,
                    summary.successful_attacks,
                    summary.duration_ms,
                    summary_json,
                    summary.started_at.isoformat(),
                    summary.completed_at.isoformat() if summary.completed_at else None,
                ),
            )

    def get_run(self, run_id: str) -> RunSummary | None:
        conn = _get_conn(self.db_path)
        row = conn.execute("SELECT summary_json FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if not row:
            return None
        return RunSummary.model_validate_json(row["summary_json"])

    def list_runs(self, limit: int = 50) -> list[dict]:
        conn = _get_conn(self.db_path)
        rows = conn.execute(
            """
            SELECT run_id, target_name, target_mode, status, overall_asr,
                   wilson_lower, wilson_upper, risk_grade, total_scenarios,
                   total_trials, successful_attacks, duration_ms, started_at, completed_at
            FROM runs ORDER BY started_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def save_report(self, run_id: str, report_format: str, content: str) -> None:
        from vantage.models.domain import now_utc

        with self._tx() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO reports (run_id, format, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (run_id, report_format.lower(), content, now_utc().isoformat()),
            )

    def get_report(self, run_id: str, report_format: str) -> str | None:
        conn = _get_conn(self.db_path)
        row = conn.execute(
            "SELECT content FROM reports WHERE run_id = ? AND format = ?",
            (run_id, report_format.lower()),
        ).fetchone()
        return row["content"] if row else None


_db_singleton: Database | None = None


def get_db(db_path: Path | None = None) -> Database:
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = Database(db_path)
    return _db_singleton
