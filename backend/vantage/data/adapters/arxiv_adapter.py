"""arXiv adapter — public Atom feed, no API key required."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

from vantage.data.adapters.base import SourceAdapter
from vantage.models.domain import Entity, EntityType, MetricType, Observation

_NS = {"atom": "http://www.w3.org/2005/Atom"}
_CATEGORIES = ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "stat.ML"]
_BASE = "https://export.arxiv.org/api/query"


class ArXivAdapter(SourceAdapter):
    adapter_id = "arxiv"
    _rate_limit_rps = 0.4

    async def fetch(self) -> list[dict[str, Any]]:
        results: list[dict] = []
        seen: set[str] = set()
        for cat in _CATEGORIES:
            try:
                resp = await self._get(
                    _BASE,
                    params={
                        "search_query": f"cat:{cat}",
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                        "max_results": 20,
                    },
                )
                root = ET.fromstring(resp.text)
                for entry in root.findall("atom:entry", _NS):
                    id_el = entry.find("atom:id", _NS)
                    if id_el is None:
                        continue
                    arxiv_id = id_el.text.strip().split("/")[-1]
                    if arxiv_id not in seen:
                        seen.add(arxiv_id)
                        results.append({"entry": entry, "category": cat})
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(f"arxiv {cat}: {exc}")
        return results

    async def normalize(
        self, raw: list[dict[str, Any]]
    ) -> tuple[list[Entity], list[Observation]]:
        entities: list[Entity] = []
        observations: list[Observation] = []
        now = datetime.now(timezone.utc)

        for item in raw:
            entry = item["entry"]
            id_el = entry.find("atom:id", _NS)
            if id_el is None:
                continue
            arxiv_id = id_el.text.strip().split("/")[-1]
            title_el = entry.find("atom:title", _NS)
            title = (
                " ".join((title_el.text or "").split())
                if title_el is not None
                else arxiv_id
            )
            summary_el = entry.find("atom:summary", _NS)
            abstract = (
                (summary_el.text or "")[:800].strip()
                if summary_el is not None
                else ""
            )
            published_el = entry.find("atom:published", _NS)
            published_str = (
                published_el.text.strip()
                if published_el is not None
                else now.isoformat()
            )
            authors = [
                a.find("atom:name", _NS).text
                for a in entry.findall("atom:author", _NS)
                if a.find("atom:name", _NS) is not None
            ]

            entity = Entity(
                name=f"arxiv:{arxiv_id}",
                entity_type=EntityType.PAPER,
                primary_url=f"https://arxiv.org/abs/{arxiv_id}",
                description=title[:500],
                domain="technology",
                metadata={
                    "arxiv_id": arxiv_id,
                    "category": item["category"],
                    "abstract": abstract[:400],
                    "authors": authors[:5],
                    "published": published_str,
                },
            )
            entities.append(entity)
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.MENTIONS.value,
                    metric_value=1.0,
                    observed_at=now,
                    collected_at=now,
                )
            )

        return entities, observations
