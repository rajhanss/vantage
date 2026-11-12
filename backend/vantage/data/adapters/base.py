"""Abstract source adapter base class with rate limiting and retry."""
from __future__ import annotations

import asyncio
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from vantage.core.logging import get_logger
from vantage.models.domain import Entity, Observation

log = get_logger(__name__)

DEFAULT_TIMEOUT = 25.0
DEFAULT_BACKOFF = [1, 3, 7]


class SourceAdapter(ABC):
    adapter_id: str = "base"
    _rate_limit_rps: float = 2.0

    def __init__(self) -> None:
        self._last_request: float = 0.0
        self._client: httpx.AsyncClient | None = None

    async def _client_ctx(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=DEFAULT_TIMEOUT,
                headers={
                    "User-Agent": (
                        "Vantage/0.1 intelligence-platform "
                        "(https://github.com/rajhanss/vantage)"
                    )
                },
                follow_redirects=True,
            )
        return self._client

    async def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        await self._rate_limit()
        client = await self._client_ctx()
        last_exc: Exception | None = None
        for delay in DEFAULT_BACKOFF + [None]:  # type: ignore[list-item]
            try:
                resp = await client.get(url, **kwargs)
                resp.raise_for_status()
                return resp
            except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                if delay is None:
                    break
                log.warning(
                    "adapter.retry",
                    adapter=self.adapter_id,
                    url=url,
                    error=str(exc),
                    retry_in=delay,
                )
                await asyncio.sleep(delay)
        raise RuntimeError(f"{self.adapter_id} GET {url} failed: {last_exc}")

    async def _rate_limit(self) -> None:
        min_interval = 1.0 / max(self._rate_limit_rps, 0.01)
        elapsed = time.monotonic() - self._last_request
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        self._last_request = time.monotonic()

    @abstractmethod
    async def fetch(self) -> list[dict[str, Any]]:
        """Fetch raw records from the source."""

    @abstractmethod
    async def normalize(
        self, raw: list[dict[str, Any]]
    ) -> tuple[list[Entity], list[Observation]]:
        """Normalize raw records into domain objects."""

    async def run(self) -> tuple[list[Entity], list[Observation]]:
        log.info("adapter.start", adapter=self.adapter_id)
        try:
            raw = await self.fetch()
            entities, observations = await self.normalize(raw)
            log.info(
                "adapter.done",
                adapter=self.adapter_id,
                entities=len(entities),
                observations=len(observations),
            )
            return entities, observations
        except Exception as exc:
            log.error("adapter.error", adapter=self.adapter_id, error=str(exc))
            return [], []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @staticmethod
    def dedup_hash(*parts: Any) -> str:
        payload = "|".join(str(p) for p in parts).encode()
        return hashlib.sha256(payload).hexdigest()[:16]
