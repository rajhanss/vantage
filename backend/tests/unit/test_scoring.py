"""Unit tests for Wilson score intervals and statistical scoring."""
from __future__ import annotations

import pytest

from vantage.models.domain import RiskGrade
from vantage.scoring.calculator import compute_risk_grade, compute_wilson_interval


def test_wilson_interval_known_inputs():
    # 0 successes out of 10 trials
    low, high = compute_wilson_interval(0, 10)
    assert low == 0.0
    assert 0.27 <= high <= 0.29

    # 10 successes out of 10 trials
    low, high = compute_wilson_interval(10, 10)
    assert 0.71 <= low <= 0.73
    assert high == 1.0

    # 5 successes out of 10 trials (p = 0.5)
    low, high = compute_wilson_interval(5, 10)
    assert 0.23 <= low <= 0.25
    assert 0.75 <= high <= 0.77

    # 0 trials edge case
    assert compute_wilson_interval(0, 0) == (0.0, 0.0)


def test_risk_grade_boundaries():
    assert compute_risk_grade(0.0) == RiskGrade.A
    assert compute_risk_grade(0.04) == RiskGrade.A
    assert compute_risk_grade(0.05) == RiskGrade.B
    assert compute_risk_grade(0.19) == RiskGrade.B
    assert compute_risk_grade(0.20) == RiskGrade.C
    assert compute_risk_grade(0.39) == RiskGrade.C
    assert compute_risk_grade(0.40) == RiskGrade.D
    assert compute_risk_grade(0.69) == RiskGrade.D
    assert compute_risk_grade(0.70) == RiskGrade.F
    assert compute_risk_grade(1.0) == RiskGrade.F
