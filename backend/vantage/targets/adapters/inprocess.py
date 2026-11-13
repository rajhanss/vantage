"""In-process target adapter for Vantage testbeds and direct Python agents."""
from __future__ import annotations

from typing import Any

from vantage.models.domain import TargetResponse, TargetSpec, TranscriptEntry
from vantage.targets.base import Target
from vantage.targets.canary_toolkit import CanaryRecorder
from vantage.testbed.toy_agent import ToyAgentTarget


class InProcessTargetAdapter(Target):
    """Executes target agent directly in-process with zero network latency."""

    def __init__(self, spec: TargetSpec, recorder: CanaryRecorder | None = None) -> None:
        self.spec = spec
        self.recorder = recorder or CanaryRecorder()
        self.agent = ToyAgentTarget(mode=spec.mode, recorder=self.recorder)

    async def reset(self, seed: int | None = None) -> None:
        await self.agent.reset(seed)

    async def send_message(self, message: str) -> TargetResponse:
        return await self.agent.send_message(message)

    async def send_tool_result(self, call_id: str, output: str) -> TargetResponse:
        return await self.agent.send_tool_result(call_id, output)

    async def get_history(self) -> list[TranscriptEntry]:
        return await self.agent.get_history()

    async def close(self) -> None:
        await self.agent.close()
