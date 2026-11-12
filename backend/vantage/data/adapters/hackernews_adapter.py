"""HackerNews adapter — official Firebase REST API."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from vantage.data.adapters.base import SourceAdapter
from vantage.models.domain import Entity, EntityType, MetricType, Observation

_BASE = "https://hacker-news.firebaseio.com/v0"


class HackerNewsAdapter(SourceAdapter):
    adapter_id = "hackernews"
    _rate_limit_rps = 4.0

    async def fetch(self) -> list[dict[str, Any]]:
        try:
            resp = await self._get(f"{_BASE}/topstories.json")
            story_ids: list[int] = resp.json()[:80]
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"hn topstories fail: {exc}")
            return []

        # Fetch items in batches of 10 to avoid hammering
        results: list[dict] = []
        for i in range(0, min(len(story_ids), 60), 10):
            batch = story_ids[i : i + 10]
            tasks = [self._fetch_item(sid) for sid in batch]
            items = await asyncio.gather(*tasks, return_exceptions=True)
            for item in items:
                if isinstance(item, dict) and item.get("type") == "story":
                    results.append(item)

        return results

    async def _fetch_item(self, item_id: int) -> dict | None:
        try:
            r = await self._get(f"{_BASE}/item/{item_id}.json")
            return r.json()
        except Exception:
            return None

    async def normalize(
        self, raw: list[dict[str, Any]]
    ) -> tuple[list[Entity], list[Observation]]:
        entities: list[Entity] = []
        observations: list[Observation] = []
        now = datetime.now(timezone.utc)

        for item in raw:
            if not item:
                continue
            item_id = str(item.get("id", ""))
            title = (item.get("title") or "")[:300]
            if not item_id or not title:
                continue

            entity = Entity(
                name=f"hn:{item_id}",
                entity_type=EntityType.TOPIC,
                primary_url=(
                    item.get("url")
                    or f"https://news.ycombinator.com/item?id={item_id}"
                ),
                description=title,
                domain="technology",
                metadata={
                    "hn_id": item_id,
                    "by": item.get("by", ""),
                    "time": item.get("time", 0),
                    "url": item.get("url", ""),
                    "type": "story",
                },
            )
            entities.append(entity)

            score = float(item.get("score") or 0)
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.ENGAGEMENT.value,
                    metric_value=score,
                    observed_at=now,
                    collected_at=now,
                )
            )
            comments = float(item.get("descendants") or 0)
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.COMMENT_COUNT.value,
                    metric_value=comments,
                    observed_at=now,
                    collected_at=now,
                )
            )

        return entities, observations
