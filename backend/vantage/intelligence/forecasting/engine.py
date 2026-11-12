"""Time-series forecasting — damped Holt-Winters with quantile PI bands."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from vantage.models.domain import ForecastPoint, Observation, TrendForecast

_PHI = 0.95  # Damping factor
_ALPHA = 0.3  # Level smoothing
_BETA = 0.1   # Trend smoothing


def _holt_winters(
    values: list[float],
    alpha: float = _ALPHA,
    beta: float = _BETA,
    phi: float = _PHI,
) -> tuple[float, float]:
    """
    Damped additive Holt-Winters single-variate smoothing.
    Returns (level, damped_trend) after processing all observations.
    """
    if len(values) < 2:
        return values[0] if values else 0.0, 0.0

    l_t = values[0]
    b_t = values[1] - values[0]

    for v in values[2:]:
        l_prev, b_prev = l_t, b_t
        l_t = alpha * v + (1.0 - alpha) * (l_prev + phi * b_prev)
        b_t = beta * (l_t - l_prev) + (1.0 - beta) * phi * b_prev

    return l_t, b_t


def _phi_sum(phi: float, h: int) -> float:
    """Sum of phi^1 + phi^2 + ... + phi^h (damped trend accumulator)."""
    return sum(phi ** k for k in range(1, h + 1))


def _compute_residuals(values: list[float]) -> list[float]:
    """One-step-ahead residuals from Holt-Winters for PI estimation."""
    if len(values) < 3:
        return [0.0]

    residuals: list[float] = []
    for i in range(2, len(values)):
        l, b = _holt_winters(values[:i])
        forecasted = l + b * _phi_sum(_PHI, 1)
        residuals.append(values[i] - forecasted)

    return residuals if residuals else [0.0]


def forecast_entity(
    observations: list[Observation],
    horizon_days: int = 30,
) -> TrendForecast:
    """
    Forecast future values for an entity using damped Holt-Winters.
    Prediction intervals estimated from rolling residual quantiles.
    """
    entity_id = observations[0].entity_id if observations else ""
    sorted_obs = sorted(observations, key=lambda o: o.observed_at)
    values = [o.metric_value for o in sorted_obs]

    if not values:
        return TrendForecast(entity_id=entity_id, horizon_days=horizon_days)

    if len(values) < 2:
        return TrendForecast(
            entity_id=entity_id,
            horizon_days=horizon_days,
            points=_flat_forecast(values[0], horizon_days),
        )

    l_t, b_t = _holt_winters(values)
    residuals = sorted(_compute_residuals(values))
    n = len(residuals)

    def quantile(q: float) -> float:
        idx = max(0, min(n - 1, int(q * n)))
        return residuals[idx]

    q_10, q_90 = quantile(0.10), quantile(0.90)
    q_025, q_975 = quantile(0.025), quantile(0.975)

    # MAPE on last 20% of historical data
    mape = 0.0
    test_size = max(2, len(values) // 5)
    if len(values) > test_size + 2:
        train = values[:-test_size]
        test = values[-test_size:]
        l_tr, b_tr = _holt_winters(train)
        abs_pct_errors: list[float] = []
        for h, actual in enumerate(test, start=1):
            pred = max(0.0, l_tr + b_tr * _phi_sum(_PHI, h))
            abs_pct_errors.append(abs(actual - pred) / (abs(actual) + 1e-9))
        mape = sum(abs_pct_errors) / len(abs_pct_errors)

    today = datetime.now(timezone.utc)
    points: list[ForecastPoint] = []
    for h in range(1, horizon_days + 1):
        phi_h = _phi_sum(_PHI, h)
        predicted = max(0.0, l_t + b_t * phi_h)
        date_str = (today + timedelta(days=h)).strftime("%Y-%m-%d")
        l80 = min(predicted, predicted + q_10)
        u80 = max(predicted, predicted + q_90)
        l95 = min(l80, predicted + q_025)
        u95 = max(u80, predicted + q_975)
        points.append(
            ForecastPoint(
                date=date_str,
                value=round(predicted, 2),
                lower_80=round(max(0.0, l80), 2),
                upper_80=round(max(0.0, u80), 2),
                lower_95=round(max(0.0, l95), 2),
                upper_95=round(max(0.0, u95), 2),
            )
        )

    return TrendForecast(
        entity_id=entity_id,
        horizon_days=horizon_days,
        historical_mape=round(mape, 4),
        points=points,
    )


def _flat_forecast(value: float, horizon: int) -> list[ForecastPoint]:
    today = datetime.now(timezone.utc)
    band = value * 0.1
    return [
        ForecastPoint(
            date=(today + timedelta(days=h)).strftime("%Y-%m-%d"),
            value=round(value, 2),
            lower_80=round(max(0.0, value - band), 2),
            upper_80=round(value + band, 2),
            lower_95=round(max(0.0, value - band * 2), 2),
            upper_95=round(value + band * 2, 2),
        )
        for h in range(1, horizon + 1)
    ]
