"""PyPI adapter — public JSON API and pypistats download data."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from vantage.data.adapters.base import SourceAdapter
from vantage.models.domain import Entity, EntityType, MetricType, Observation

_PACKAGES = [
    "transformers", "torch", "tensorflow", "langchain", "openai", "anthropic",
    "fastapi", "pydantic", "uvicorn", "httpx", "numpy", "pandas", "scikit-learn",
    "huggingface-hub", "diffusers", "accelerate", "datasets", "tokenizers",
    "gradio", "streamlit", "sentence-transformers", "chromadb", "faiss-cpu",
    "llama-index", "langsmith", "groq", "mistralai", "litellm", "dspy-ai",
    "vllm", "trl", "peft", "einops", "timm", "xformers",
]


class PyPIAdapter(SourceAdapter):
    adapter_id = "pypi"
    _rate_limit_rps = 1.5
    _INFO_URL = "https://pypi.org/pypi/{pkg}/json"
    _STATS_URL = "https://pypistats.org/api/packages/{pkg}/recent"

    async def fetch(self) -> list[dict[str, Any]]:
        results: list[dict] = []
        for pkg in _PACKAGES:
            try:
                info_resp = await self._get(self._INFO_URL.format(pkg=pkg))
                info = info_resp.json().get("info", {})
                try:
                    stats_resp = await self._get(self._STATS_URL.format(pkg=pkg))
                    stats = stats_resp.json().get("data", {})
                except Exception:
                    stats = {}
                results.append({"info": info, "stats": stats, "pkg": pkg})
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(f"pypi {pkg}: {exc}")
        return results

    async def normalize(
        self, raw: list[dict[str, Any]]
    ) -> tuple[list[Entity], list[Observation]]:
        entities: list[Entity] = []
        observations: list[Observation] = []
        now = datetime.now(timezone.utc)

        for item in raw:
            info = item.get("info", {})
            stats = item.get("stats", {})
            pkg_name = info.get("name") or item.get("pkg", "")
            if not pkg_name:
                continue

            entity = Entity(
                name=pkg_name,
                entity_type=EntityType.PACKAGE,
                primary_url=f"https://pypi.org/project/{pkg_name}/",
                description=(info.get("summary") or "")[:400],
                domain="technology",
                metadata={
                    "version": info.get("version", ""),
                    "author": info.get("author", ""),
                    "home_page": info.get("home_page", ""),
                    "requires_python": info.get("requires_python", ""),
                    "classifiers": (info.get("classifiers") or [])[:5],
                },
            )
            entities.append(entity)

            monthly = float(
                stats.get("last_month")
                or stats.get("last_week", 0)
                or 0
            )
            observations.append(
                Observation(
                    entity_id=entity.id,
                    source_id=self.adapter_id,
                    metric_name=MetricType.DOWNLOADS.value,
                    metric_value=monthly,
                    observed_at=now,
                    collected_at=now,
                )
            )

        return entities, observations
