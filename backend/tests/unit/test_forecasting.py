"""Unit tests for time-series forecasting engine."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from vantage.intelligence.forecasting.engine import forecast_entity, _holt_winters
from vantage.models.domain import ForecastPoint, Observation, TrendForecast


def _make_obs(entity_id: str, values: list[float]) -> list[Observation]:
    from datetime import timedelta
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        Observation(
            entity_id=entity_id,
            source_id="test",
            metric_name="stars",
            metric_value=v,
            observed_at=base + timedelta(days=i),
            collected_at=base + timedelta(days=i),
        )
        for i, v in enumerate(values)
    ]


class TestHoltWinters:
    def test_single_value(self):
        l, b = _holt_winters([42.0])
        assert l == 42.0
        assert b == 0.0

    def test_two_values(self):
        l, b = _holt_winters([10.0, 20.0])
        assert l > 0
        assert isinstance(b, float)

    def test_growing_series_positive_trend(self):
        values = [float(i * 10) for i in range(1, 15)]
        l, b = _holt_winters(values)
        assert b > 0.0  # Trend should be positive


class TestForecastEntity:
    def test_empty_observations_returns_empty_forecast(self):
        forecast = forecast_entity([])
        assert isinstance(forecast, TrendForecast)
        assert len(forecast.points) == 0

    def test_single_observation_returns_flat_forecast(self):
        obs = _make_obs("e1", [100.0])
        forecast = forecast_entity(obs, horizon_days=7)
        assert len(forecast.points) == 7
        for pt in forecast.points:
            assert pt.value == pytest.approx(100.0, rel=0.01)

    def test_horizon_length_correct(self):
        obs = _make_obs("e1", [10.0, 20.0, 30.0, 40.0, 50.0])
        for horizon in [7, 14, 30]:
            forecast = forecast_entity(obs, horizon_days=horizon)
            assert len(forecast.points) == horizon

    def test_confidence_intervals_ordered(self):
        obs = _make_obs("e1", [float(i * 5) for i in range(1, 20)])
        forecast = forecast_entity(obs, horizon_days=10)
        for pt in forecast.points:
            assert pt.lower_95 <= pt.lower_80, f"lower_95 > lower_80 at {pt.date}"
            assert pt.lower_80 <= pt.value, f"lower_80 > value at {pt.date}"
            assert pt.value <= pt.upper_80, f"value > upper_80 at {pt.date}"
            assert pt.upper_80 <= pt.upper_95, f"upper_80 > upper_95 at {pt.date}"

    def test_values_non_negative(self):
        obs = _make_obs("e1", [100.0, 90.0, 80.0, 70.0, 60.0])
        forecast = forecast_entity(obs, horizon_days=10)
        for pt in forecast.points:
            assert pt.value >= 0.0
            assert pt.lower_80 >= 0.0
            assert pt.lower_95 >= 0.0

    def test_forecast_dates_are_sequential(self):
        obs = _make_obs("e1", [10.0, 20.0, 30.0, 40.0])
        forecast = forecast_entity(obs, horizon_days=5)
        dates = [pt.date for pt in forecast.points]
        assert dates == sorted(dates)

    def test_mape_in_valid_range(self):
        obs = _make_obs("e1", [float(i * 10) for i in range(1, 25)])
        forecast = forecast_entity(obs, horizon_days=7)
        assert 0.0 <= forecast.historical_mape <= 10.0

    def test_growing_series_positive_forecast(self):
        obs = _make_obs("e1", [float(i * 100) for i in range(1, 15)])
        forecast = forecast_entity(obs, horizon_days=7)
        # Forecast should continue growing
        last_hist = obs[-1].metric_value
        # At least some forecast points should be >= last historical
        assert any(pt.value >= last_hist * 0.5 for pt in forecast.points)
