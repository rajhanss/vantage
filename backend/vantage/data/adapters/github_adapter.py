"""GitHub public search adapter — no authentication required."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from vantage.data.adapters.base import SourceAdapter
from vantage.models.domain import Entity, EntityType, MetricType, Observation

_QUERIES = [
    "stars:>500 pushed:>2024-06-01 language:Python",
    "stars:>500 pushed:>2024-06-01 language:TypeScript",
    "stars:>200 topic:llm",
    "stars:>200 topic:machine-learning pushed:>2024-01-01",
    "stars:>100 topic:ai-agent",
]


class GitHubAdapter(SourceAdapter):
    adapter_id = "github"
    _rate_limit_rps = 0.8
    _SEARCH_URL = "https://api.github.com/search/repositories"

    async def fetch(self) -> list[dict[str, Any]]:
        results: list[dict] = []
        seen: set[str] = set()
        for q in _QUERIES:
            try:
                resp = await self._get(
                    self._SEARCH_URL,
                    params={"q": q, "sort": "stars", "order": "desc", "per_page": 25},
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                for item in resp.json().get("items", []):
                    full_name = item.get("full_name", "")
                    if full_name and full_name not in seen:
                        seen.add(full_name)
                        results.append(item)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(f"github query failed '{q}': {exc}")
        return results

    async def normalize(
        self, raw: list[dict[str, Any]]
    ) -> tuple[list[Entity], list[Observation]]:
        entities: list[Entity] = []
        observations: list[Observation] = []
        now = datetime.now(timezone.utc)
        seen: set[str] = set()

        for item in raw:
            full_name = item.get("full_name", "")
            if not full_name or full_name in seen:
                continue
            seen.add(full_name)

            entity = Entity(
                name=full_name,
                entity_type=EntityType.REPOSITORY,
                primary_url=item.get("html_url", f"https://github.com/{full_name}"),
                description=(item.get("description") or "")[:500],
                domain="technology",
                metadata={
                    "language": item.get("language", ""),
                    "topics": item.get("topics", [])[:10],
                    "forks": item.get("forks_count", 0),
                    "open_issues": item.get("open_issues_count", 0),
                    "created_at": item.get("created_at", ""),
                    "pushed_at": item.get("pushed_at", ""),
                    "default_branch": item.get("default_branch", "main"),
                },
            )
            entities.append(entity)

            stars = float(item.get("stargazers_count") or 0)
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.STARS.value,
                    metric_value=stars,
                    observed_at=now,
                    collected_at=now,
                )
            )
            forks = float(item.get("forks_count") or 0)
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.FORKS.value,
                    metric_value=forks,
                    observed_at=now,
                    collected_at=now,
                )
            )

        return entities, observations
