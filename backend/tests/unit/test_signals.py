"""Unit tests for signal detection engine."""
from __future__ import annotations

import pytest
from vantage.intelligence.signals.detector import (
    compute_acceleration,
    compute_rolling_z_score,
    compute_velocity,
)


class TestComputeVelocity:
    def test_empty_returns_zero(self):
        assert compute_velocity([]) == 0.0

    def test_single_returns_zero(self):
        assert compute_velocity([100.0]) == 0.0

    def test_flat_series_returns_zero(self):
        assert compute_velocity([50.0, 50.0, 50.0, 50.0]) == 0.0

    def test_linear_growth(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        assert compute_velocity(values) == pytest.approx(10.0)

    def test_negative_velocity(self):
        values = [100.0, 80.0, 60.0, 40.0, 20.0]
        assert compute_velocity(values) < 0.0

    def test_uses_last_seven_deltas(self):
        # Long series: early growth then stabilisation
        early = [float(i * 100) for i in range(10)]
        stable = [1000.0] * 8
        values = early + stable
        # Recent velocity should be near 0
        assert abs(compute_velocity(values)) < 1.0


class TestComputeAcceleration:
    def test_empty_returns_zero(self):
        assert compute_acceleration([]) == 0.0

    def test_two_values_returns_zero(self):
        assert compute_acceleration([10.0, 20.0]) == 0.0

    def test_linear_growth_zero_acceleration(self):
        values = [float(i) for i in range(20)]
        assert abs(compute_acceleration(values)) < 1e-9

    def test_positive_acceleration(self):
        # Exponential-ish growth should produce positive acceleration
        values = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
        assert compute_acceleration(values) > 0.0

    def test_deceleration(self):
        # Growth slowing
        values = [100.0, 180.0, 240.0, 280.0, 300.0]
        assert compute_acceleration(values) < 0.0


class TestComputeRollingZScore:
    def test_empty_returns_zero(self):
        assert compute_rolling_z_score([]) == 0.0

    def test_one_value_returns_zero(self):
        assert compute_rolling_z_score([42.0]) == 0.0

    def test_two_values_returns_zero(self):
        assert compute_rolling_z_score([10.0, 20.0]) == 0.0

    def test_flat_baseline_zero_std_returns_zero(self):
        values = [100.0, 100.0, 100.0, 100.0, 100.0]
        assert compute_rolling_z_score(values) == 0.0

    def test_extreme_spike_above_threshold(self):
        baseline = [100.0] * 20
        spike = baseline + [1000.0]
        z = compute_rolling_z_score(spike, window=14)
        assert z > 2.5

    def test_negative_spike(self):
        baseline = [1000.0] * 20
        crash = baseline + [100.0]
        z = compute_rolling_z_score(crash, window=14)
        assert z < -2.5

    def test_moderate_growth_low_z(self):
        values = [float(i * 10) for i in range(1, 16)]
        z = compute_rolling_z_score(values, window=14)
        # Gradual linear growth should produce low Z (not an anomaly)
        assert abs(z) < 2.5
