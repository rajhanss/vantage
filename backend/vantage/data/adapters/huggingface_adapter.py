"""HuggingFace Hub adapter — public REST API, no authentication."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from vantage.data.adapters.base import SourceAdapter
from vantage.models.domain import Entity, EntityType, MetricType, Observation


class HuggingFaceAdapter(SourceAdapter):
    adapter_id = "huggingface"
    _rate_limit_rps = 1.0
    _MODELS_URL = "https://huggingface.co/api/models"
    _DATASETS_URL = "https://huggingface.co/api/datasets"

    async def fetch(self) -> list[dict[str, Any]]:
        results: list[dict] = []
        requests = [
            (self._MODELS_URL, {"sort": "downloads", "limit": 40, "full": "false"}),
            (self._MODELS_URL, {"sort": "likes7d", "limit": 30, "full": "false"}),
            (self._DATASETS_URL, {"sort": "downloads", "limit": 20, "full": "false"}),
        ]
        seen: set[str] = set()
        for url, params in requests:
            try:
                resp = await self._get(url, params=params)
                for item in resp.json():
                    item_id = item.get("modelId") or item.get("id", "")
                    if item_id and item_id not in seen:
                        seen.add(item_id)
                        results.append(item)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(f"hf fetch failed: {exc}")
        return results

    async def normalize(
        self, raw: list[dict[str, Any]]
    ) -> tuple[list[Entity], list[Observation]]:
        entities: list[Entity] = []
        observations: list[Observation] = []
        now = datetime.now(timezone.utc)

        for item in raw:
            model_id = item.get("modelId") or item.get("id", "")
            if not model_id:
                continue

            entity = Entity(
                name=model_id,
                entity_type=EntityType.MODEL,
                primary_url=f"https://huggingface.co/{model_id}",
                description="",
                domain="technology",
                metadata={
                    "pipeline_tag": item.get("pipeline_tag", ""),
                    "tags": (item.get("tags") or [])[:10],
                    "library_name": item.get("library_name", ""),
                    "private": item.get("private", False),
                    "gated": item.get("gated", False),
                },
            )
            entities.append(entity)

            downloads = float(item.get("downloads") or 0)
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.DOWNLOADS.value,
                    metric_value=downloads,
                    observed_at=now,
                    collected_at=now,
                )
            )
            likes = float(item.get("likes") or 0)
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.ENGAGEMENT.value,
                    metric_value=likes,
                    observed_at=now,
                    collected_at=now,
                )
            )

        return entities, observations
