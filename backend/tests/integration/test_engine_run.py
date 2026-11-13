"""Integration tests for Vantage evaluation engine."""
from __future__ import annotations

import pytest

from vantage.engine.runner import AsyncRunner
from vantage.models.domain import (
    OwaspCategory,
    RiskGrade,
    RunConfig,
    RunStatus,
    TargetSpec,
    TargetType,
)
from vantage.scoring.calculator import compare_runs


@pytest.mark.asyncio
async def test_full_evaluation_vulnerable_target():
    config = RunConfig(
        target_spec=TargetSpec(
            name="Testbed-Vulnerable",
            type=TargetType.IN_PROCESS,
            mode="vulnerable",
        ),
        selected_categories=[OwaspCategory.ASI01, OwaspCategory.ASI02, OwaspCategory.ASI03],
        trials_per_scenario=2,
        seed=100,
    )

    runner = AsyncRunner(config=config)
    summary = await runner.run()

    assert summary.status == RunStatus.COMPLETED
    assert summary.total_scenarios > 0
    assert summary.total_trials > 0
    # Vulnerable agent should succumb to attacks
    assert summary.successful_attacks > 0
    assert summary.overall_asr > 0.5
    assert summary.risk_grade in (RiskGrade.D, RiskGrade.F)
    assert len(summary.findings) > 0


@pytest.mark.asyncio
async def test_full_evaluation_hardened_target():
    config = RunConfig(
        target_spec=TargetSpec(
            name="Testbed-Hardened",
            type=TargetType.IN_PROCESS,
            mode="hardened",
        ),
        selected_categories=[OwaspCategory.ASI01, OwaspCategory.ASI02, OwaspCategory.ASI03],
        trials_per_scenario=2,
        seed=200,
    )

    runner = AsyncRunner(config=config)
    summary = await runner.run()

    assert summary.status == RunStatus.COMPLETED
    # Hardened agent should resist attacks
    assert summary.successful_attacks == 0
    assert summary.overall_asr == 0.0
    assert summary.risk_grade == RiskGrade.A
    assert all(f.successful_attacks == 0 for f in summary.findings)


@pytest.mark.asyncio
async def test_run_comparison_shows_defense_efficacy():
    cfg_vuln = RunConfig(
        target_spec=TargetSpec(name="ToyAgent", mode="vulnerable"),
        selected_categories=[OwaspCategory.ASI01],
        trials_per_scenario=1,
    )
    cfg_hard = RunConfig(
        target_spec=TargetSpec(name="ToyAgent", mode="hardened"),
        selected_categories=[OwaspCategory.ASI01],
        trials_per_scenario=1,
    )

    res_vuln = await AsyncRunner(config=cfg_vuln).run()
    res_hard = await AsyncRunner(config=cfg_hard).run()

    comparison = compare_runs(res_vuln, res_hard)
    assert comparison.asr_delta > 0.0
    assert len(comparison.resolved_scenarios) > 0
    assert comparison.hardened_grade == RiskGrade.A


@pytest.mark.asyncio
async def test_runner_kill_switch_aborts_immediately():
    config = RunConfig(
        target_spec=TargetSpec(name="LongRunTarget", mode="vulnerable"),
        trials_per_scenario=5,
    )
    runner = AsyncRunner(config=config)
    runner.abort()  # Pre-abort
    summary = await runner.run()
    assert summary.status == RunStatus.CANCELLED
