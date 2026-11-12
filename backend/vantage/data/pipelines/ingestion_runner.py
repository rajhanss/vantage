"""Ingestion runner — orchestrates all adapters and runs signal detection."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from vantage.core.logging import get_logger
from vantage.data.adapters.arxiv_adapter import ArXivAdapter
from vantage.data.adapters.github_adapter import GitHubAdapter
from vantage.data.adapters.hackernews_adapter import HackerNewsAdapter
from vantage.data.adapters.huggingface_adapter import HuggingFaceAdapter
from vantage.data.adapters.pypi_adapter import PyPIAdapter
from vantage.data.storage.database import Database, get_db
from vantage.intelligence.signals.detector import SignalDetector
from vantage.models.domain import Entity, Observation

log = get_logger(__name__)

_ADAPTER_CLASSES = [
    GitHubAdapter,
    HuggingFaceAdapter,
    ArXivAdapter,
    HackerNewsAdapter,
    PyPIAdapter,
]


async def run_ingestion(db: Database | None = None) -> dict:
    if db is None:
        db = get_db()

    start = datetime.now(timezone.utc)
    total_entities = 0
    total_observations = 0
    total_signals = 0
    errors: list[str] = []

    for AdapterClass in _ADAPTER_CLASSES:
        adapter = AdapterClass()
        try:
            entities, observations = await adapter.run()

            # Persist entities and build id-remap (upsert may change effective id)
            entity_id_remap: dict[str, str] = {}
            for entity in entities:
                try:
                    db.upsert_entity(entity)
                    resolved = db.get_entity_by_name(
                        entity.name, entity.entity_type.value
                    )
                    if resolved:
                        entity_id_remap[entity.id] = resolved.id
                        total_entities += 1
                except Exception as e:
                    errors.append(f"{adapter.adapter_id}.entity({entity.name}): {e}")

            # Persist observations — remap to resolved entity ids
            for obs in observations:
                resolved_id = entity_id_remap.get(obs.entity_id, obs.entity_id)
                obs_to_save = obs.model_copy(update={"entity_id": resolved_id})
                try:
                    db.insert_observation(obs_to_save)
                    total_observations += 1
                except Exception as e:
                    errors.append(f"{adapter.adapter_id}.obs: {e}")

        except Exception as exc:
            errors.append(f"{AdapterClass.adapter_id}: {exc}")
            log.error(
                "ingestion.adapter_failed",
                adapter=AdapterClass.adapter_id,
                error=str(exc),
            )
        finally:
            await adapter.close()

    # --- Signal detection pass ---
    detector = SignalDetector(db)
    entities_all = db.list_entities(limit=1000)
    for entity in entities_all:
        try:
            signal = detector.detect_for_entity(entity)
            if signal:
                db.upsert_signal(signal)
                total_signals += 1
        except Exception as e:
            errors.append(f"signal.{entity.id[:8]}: {e}")

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    log.info(
        "ingestion.complete",
        entities=total_entities,
        observations=total_observations,
        signals=total_signals,
        elapsed_s=elapsed,
        errors=len(errors),
    )

    return {
        "entities_processed": total_entities,
        "observations_stored": total_observations,
        "signals_detected": total_signals,
        "elapsed_seconds": round(elapsed, 2),
        "errors": errors[:10],
    }
