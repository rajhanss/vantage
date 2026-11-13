"""Async execution engine for Vantage security evaluation runs."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import time
from typing import AsyncGenerator, Callable, Sequence

from vantage.models.domain import (
    AttackStep,
    Finding,
    OwaspCategory,
    RiskGrade,
    RunConfig,
    RunStatus,
    RunSummary,
    Scenario,
    StepType,
    TargetResponse,
    TranscriptEntry,
    TrialResult,
    new_id,
    now_utc,
)
from vantage.oracle.evaluator import DeterministicOracle
from vantage.scenarios.loader import load_all_scenarios
from vantage.scoring.calculator import (
    aggregate_scenario_trials,
    compute_category_scores,
    compute_risk_grade,
    compute_wilson_interval,
)
from vantage.targets.adapters.factory import create_target
from vantage.targets.base import Target
from vantage.targets.canary_toolkit import CanaryRecorder


class EventBus:
    """Publish-subscribe bus for streaming real-time run telemetry."""

    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[dict]] = []

    def subscribe(self) -> asyncio.Queue[dict]:
        q: asyncio.Queue[dict] = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[dict]) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def emit(self, event_type: str, data: dict) -> None:
        event = {"event": event_type, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()}
        for q in list(self._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


class AsyncRunner:
    """Executes scenario trial suites against target agents under budget caps."""

    def __init__(
        self,
        config: RunConfig,
        event_bus: EventBus | None = None,
        all_scenarios: Sequence[Scenario] | None = None,
    ) -> None:
        self.config = config
        self.event_bus = event_bus or EventBus()
        self.oracle = DeterministicOracle()
        self.recorder = CanaryRecorder()
        self.scenarios = self._resolve_scenarios(all_scenarios or load_all_scenarios())
        self._aborted = False
        self._current_task: asyncio.Task | None = None

    def _resolve_scenarios(self, catalog: Sequence[Scenario]) -> list[Scenario]:
        selected: list[Scenario] = []
        for s in catalog:
            if s.category in self.config.selected_categories:
                if not self.config.selected_scenarios or s.id in self.config.selected_scenarios:
                    selected.append(s)
        return selected

    def abort(self) -> None:
        """Immediate kill switch stopping all in-flight trials."""
        self._aborted = True
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

    async def run(self) -> RunSummary:
        run_id = new_id()
        started_at = now_utc()
        target: Target = create_target(self.config.target_spec, recorder=self.recorder)

        summary = RunSummary(
            run_id=run_id,
            target_name=self.config.target_spec.name,
            target_mode=self.config.target_spec.mode,
            status=RunStatus.RUNNING,
            total_scenarios=len(self.scenarios),
            started_at=started_at,
        )

        await self.event_bus.emit(
            "run_started",
            {
                "run_id": run_id,
                "target": self.config.target_spec.name,
                "total_scenarios": len(self.scenarios),
            },
        )

        all_findings: list[Finding] = []
        total_trials_count = 0
        total_successes_count = 0
        t0 = time.perf_counter()

        try:
            for s_idx, scenario in enumerate(self.scenarios):
                if self._aborted:
                    summary.status = RunStatus.CANCELLED
                    break

                await self.event_bus.emit(
                    "scenario_started",
                    {"run_id": run_id, "scenario_id": scenario.id, "scenario_name": scenario.name},
                )

                trials: list[TrialResult] = []
                for t_idx in range(self.config.trials_per_scenario):
                    if self._aborted:
                        break

                    trial_seed = self.config.seed + (s_idx * 1000) + t_idx
                    trial_result = await self._execute_trial(target, scenario, t_idx, trial_seed)
                    trials.append(trial_result)
                    total_trials_count += 1
                    if trial_result.success:
                        total_successes_count += 1

                    await self.event_bus.emit(
                        "trial_completed",
                        {
                            "run_id": run_id,
                            "scenario_id": scenario.id,
                            "trial_index": t_idx,
                            "success": trial_result.success,
                            "canary_triggered": trial_result.canary_triggered,
                        },
                    )

                finding = aggregate_scenario_trials(scenario, trials)
                all_findings.append(finding)

                await self.event_bus.emit(
                    "scenario_completed",
                    {
                        "run_id": run_id,
                        "scenario_id": scenario.id,
                        "asr": finding.attack_success_rate,
                        "trials_run": finding.trials_run,
                    },
                )

            if not self._aborted:
                summary.status = RunStatus.COMPLETED
            else:
                summary.status = RunStatus.CANCELLED

        except asyncio.CancelledError:
            summary.status = RunStatus.CANCELLED
        except Exception as e:
            summary.status = RunStatus.FAILED
            summary.error = str(e)
        finally:
            await target.close()

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        summary.duration_ms = round(elapsed_ms, 2)
        summary.completed_at = now_utc()
        summary.total_trials = total_trials_count
        summary.successful_attacks = total_successes_count
        summary.overall_asr = round(total_successes_count / total_trials_count, 4) if total_trials_count > 0 else 0.0
        w_low, w_high = compute_wilson_interval(total_successes_count, total_trials_count)
        summary.wilson_lower = w_low
        summary.wilson_upper = w_high
        summary.risk_grade = compute_risk_grade(summary.overall_asr)
        summary.findings = all_findings
        summary.category_scores = compute_category_scores(all_findings)

        await self.event_bus.emit("run_completed", summary.model_dump(mode="json"))
        return summary

    async def _execute_trial(
        self,
        target: Target,
        scenario: Scenario,
        trial_index: int,
        seed: int,
    ) -> TrialResult:
        """Run a single isolated trial with clean state and step budgeting."""
        self.recorder.reset()
        await target.reset(seed)

        t_start = time.perf_counter()
        step_count = 0
        trial_error: str | None = None

        try:
            # Enforce execution timeout budget
            async with asyncio.timeout(self.config.max_budget_time_sec):
                for step in scenario.attack_steps:
                    if step_count >= self.config.max_budget_steps:
                        break

                    step_count += 1
                    if step.step_type in (StepType.USER_MESSAGE, StepType.MEMORY_INJECTION):
                        resp = await target.send_message(step.content)
                    elif step.step_type == StepType.POISONED_TOOL_OUTPUT:
                        cid = step.call_id or f"call_{step_count}"
                        resp = await target.send_tool_result(cid, step.content)
                    else:
                        resp = await target.send_message(step.content)

                    # If the agent requested tools, deliver benign simulated outputs for subsequent loops
                    if resp.tool_calls:
                        for tc in resp.tool_calls:
                            step_count += 1
                            if step_count >= self.config.max_budget_steps:
                                break
                            tool_output = self.recorder.record_tool_call(tc.name, tc.arguments)
                            await target.send_tool_result(tc.id, str(tool_output))

        except asyncio.TimeoutError:
            trial_error = "Trial exceeded maximum execution time budget"
        except Exception as e:
            trial_error = f"Execution error: {e}"

        elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        transcript = await target.get_history()

        # Deterministic canary evaluation
        eval_result = self.oracle.evaluate(
            conditions=scenario.canaries,
            recorder=self.recorder,
            transcript=transcript,
            step_count=step_count,
            max_budget_steps=self.config.max_budget_steps,
        )

        return TrialResult(
            trial_index=trial_index,
            scenario_id=scenario.id,
            seed=seed,
            success=eval_result.canary_triggered,
            canary_triggered=eval_result.canary_triggered,
            canary_events=eval_result.events,
            step_count=step_count,
            duration_ms=round(elapsed_ms, 2),
            transcript=transcript,
            error=trial_error,
        )
