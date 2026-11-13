"""Target protocol and security boundaries for Vantage.

Safety rules:
- Run only against targets on an explicit operator allowlist (localhost, sandbox, inprocess).
- No network scanning, no exploit code for third-party systems, no real credentials.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable
from urllib.parse import urlparse

from vantage.models.domain import TargetResponse, TranscriptEntry


class TargetSecurityError(Exception):
    """Raised when an unauthorized or out-of-bounds target is requested."""


DEFAULT_TARGET_ALLOWLIST = {
    "localhost",
    "127.0.0.1",
    "::1",
    "testbed",
    "inprocess",
    "sandbox",
}


def validate_target_endpoint(endpoint: str, allowlist: set[str] | None = None) -> None:
    """Ensure target endpoints strictly adhere to local and sandboxed environments."""
    allowed = allowlist or DEFAULT_TARGET_ALLOWLIST

    if endpoint.startswith("inprocess://"):
        host = endpoint.replace("inprocess://", "").split("/")[0]
        if host not in allowed:
            raise TargetSecurityError(
                f"In-process target host '{host}' is not in operator allowlist: {sorted(allowed)}"
            )
        return

    if endpoint.startswith("subprocess://"):
        return

    parsed = urlparse(endpoint)
    hostname = parsed.hostname or ""
    if hostname.lower() not in allowed:
        raise TargetSecurityError(
            f"Target host '{hostname}' in '{endpoint}' is not in operator allowlist: {sorted(allowed)}"
        )


@runtime_checkable
class Target(Protocol):
    """Protocol implemented by all agent target adapters."""

    async def reset(self, seed: int | None = None) -> None:
        """Reset agent memory and conversation history for an isolated trial."""
        ...

    async def send_message(self, message: str) -> TargetResponse:
        """Send a user message or adversarial prompt to the target agent."""
        ...

    async def send_tool_result(self, call_id: str, output: str) -> TargetResponse:
        """Deliver a tool execution result (benign or poisoned) to the agent."""
        ...

    async def get_history(self) -> list[TranscriptEntry]:
        """Retrieve full transcript of the current trial session."""
        ...

    async def close(self) -> None:
        """Clean up target resources and connections."""
        ...
