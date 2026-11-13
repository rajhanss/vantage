"""Subprocess target adapter for CLI and script-based agents."""
from __future__ import annotations

import asyncio
import json
import shlex
from typing import Any

from vantage.models.domain import TargetResponse, TargetSpec, ToolCall, TranscriptEntry
from vantage.targets.base import Target


class SubprocessTargetAdapter(Target):
    """Executes a CLI agent binary or script in a subshell, communicating via JSON-lines on stdin/stdout."""

    def __init__(self, spec: TargetSpec) -> None:
        self.spec = spec
        self.command = spec.endpoint.replace("subprocess://", "")
        self.history: list[TranscriptEntry] = []
        self._process: asyncio.subprocess.Process | None = None

    async def reset(self, seed: int | None = None) -> None:
        self.history.clear()
        if self._process and self._process.returncode is None:
            try:
                self._process.terminate()
                await self._process.wait()
            except Exception:
                pass
        self._process = None

    async def _ensure_process(self) -> asyncio.subprocess.Process:
        if self._process is None or self._process.returncode is not None:
            args = shlex.split(self.command)
            self._process = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        return self._process

    async def send_message(self, message: str) -> TargetResponse:
        self.history.append(TranscriptEntry(role="user", content=message))
        proc = await self._ensure_process()
        payload = json.dumps({"type": "message", "content": message}) + "\n"

        if proc.stdin:
            proc.stdin.write(payload.encode("utf-8"))
            await proc.stdin.drain()

        line = ""
        if proc.stdout:
            try:
                raw_line = await asyncio.wait_for(proc.stdout.readline(), timeout=self.spec.timeout_sec)
                line = raw_line.decode("utf-8").strip()
            except asyncio.TimeoutError:
                return TargetResponse(content="Execution timed out waiting for CLI response")

        try:
            data = json.loads(line) if line else {}
            content = data.get("content", line)
            tool_calls = [
                ToolCall(id=t.get("id", f"call_{i}"), name=t.get("name", ""), arguments=t.get("arguments", {}))
                for i, t in enumerate(data.get("tool_calls", []))
            ]
            resp = TargetResponse(content=content, tool_calls=tool_calls, raw=data)
        except Exception:
            resp = TargetResponse(content=line)

        self.history.append(TranscriptEntry(role="assistant", content=resp.content, tool_calls=resp.tool_calls))
        return resp

    async def send_tool_result(self, call_id: str, output: str) -> TargetResponse:
        self.history.append(TranscriptEntry(role="tool", content=output, metadata={"call_id": call_id}))
        proc = await self._ensure_process()
        payload = json.dumps({"type": "tool_result", "call_id": call_id, "output": output}) + "\n"

        if proc.stdin:
            proc.stdin.write(payload.encode("utf-8"))
            await proc.stdin.drain()

        line = ""
        if proc.stdout:
            try:
                raw_line = await asyncio.wait_for(proc.stdout.readline(), timeout=self.spec.timeout_sec)
                line = raw_line.decode("utf-8").strip()
            except asyncio.TimeoutError:
                return TargetResponse(content="Execution timed out waiting for CLI tool response")

        try:
            data = json.loads(line) if line else {}
            content = data.get("content", line)
            tool_calls = [
                ToolCall(id=t.get("id", f"call_{i}"), name=t.get("name", ""), arguments=t.get("arguments", {}))
                for i, t in enumerate(data.get("tool_calls", []))
            ]
            resp = TargetResponse(content=content, tool_calls=tool_calls, raw=data)
        except Exception:
            resp = TargetResponse(content=line)

        self.history.append(TranscriptEntry(role="assistant", content=resp.content, tool_calls=resp.tool_calls))
        return resp

    async def get_history(self) -> list[TranscriptEntry]:
        return list(self.history)

    async def close(self) -> None:
        if self._process and self._process.returncode is None:
            self._process.terminate()
            await self._process.wait()
        self._process = None
