"""HTTP REST target adapter for external agent endpoints."""
from __future__ import annotations

import httpx
from typing import Any

from vantage.models.domain import TargetResponse, TargetSpec, ToolCall, TranscriptEntry
from vantage.targets.base import Target, validate_target_endpoint


class HttpTargetAdapter(Target):
    """Adapts an HTTP REST agent service to the Vantage Target protocol."""

    def __init__(self, spec: TargetSpec) -> None:
        self.spec = spec
        validate_target_endpoint(spec.endpoint)
        self.history: list[TranscriptEntry] = []
        self._client = httpx.AsyncClient(
            base_url=spec.endpoint.rstrip("/"),
            timeout=spec.timeout_sec,
            headers={"Authorization": f"Bearer {spec.auth_token}"} if spec.auth_token else {},
        )

    async def reset(self, seed: int | None = None) -> None:
        self.history.clear()
        try:
            await self._client.post("/reset", json={"seed": seed})
        except Exception:
            pass  # Optional endpoint for agents that support state reset

    async def send_message(self, message: str) -> TargetResponse:
        self.history.append(TranscriptEntry(role="user", content=message))
        try:
            resp = await self._client.post(
                "/api/v1/chat",
                json={"message": message, "history": [h.model_dump(mode="json") for h in self.history[:-1]]},
            )
            data = resp.json() if resp.status_code == 200 else {}
            content = data.get("content", data.get("response", ""))
            raw_tools = data.get("tool_calls", [])
            tool_calls = [
                ToolCall(
                    id=t.get("id", f"call_{i}"),
                    name=t.get("name", ""),
                    arguments=t.get("arguments", {}),
                )
                for i, t in enumerate(raw_tools)
            ]
            target_resp = TargetResponse(content=content, tool_calls=tool_calls, raw=data)
            self.history.append(TranscriptEntry(role="assistant", content=content, tool_calls=tool_calls))
            return target_resp
        except Exception as e:
            err_resp = TargetResponse(content=f"HTTP connection error: {e}")
            self.history.append(TranscriptEntry(role="assistant", content=err_resp.content))
            return err_resp

    async def send_tool_result(self, call_id: str, output: str) -> TargetResponse:
        self.history.append(TranscriptEntry(role="tool", content=output, metadata={"call_id": call_id}))
        try:
            resp = await self._client.post(
                "/api/v1/tool_result",
                json={"call_id": call_id, "output": output},
            )
            data = resp.json() if resp.status_code == 200 else {}
            content = data.get("content", "")
            raw_tools = data.get("tool_calls", [])
            tool_calls = [
                ToolCall(
                    id=t.get("id", f"call_{i}"),
                    name=t.get("name", ""),
                    arguments=t.get("arguments", {}),
                )
                for i, t in enumerate(raw_tools)
            ]
            target_resp = TargetResponse(content=content, tool_calls=tool_calls, raw=data)
            self.history.append(TranscriptEntry(role="assistant", content=content, tool_calls=tool_calls))
            return target_resp
        except Exception as e:
            err_resp = TargetResponse(content=f"HTTP tool result error: {e}")
            self.history.append(TranscriptEntry(role="assistant", content=err_resp.content))
            return err_resp

    async def get_history(self) -> list[TranscriptEntry]:
        return list(self.history)

    async def close(self) -> None:
        await self._client.aclose()
