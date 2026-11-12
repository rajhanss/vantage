"""Statistical signal detection engine using Z-score and velocity analysis."""
from __future__ import annotations

import statistics
from vantage.core.logging import get_logger
from vantage.data.storage.database import Database
from vantage.models.domain import (
    Entity,
    MetricType,
    Observation,
    Signal,
    SignalType,
)

log = get_logger(__name__)

Z_THRESHOLD = 2.5
WINDOW = 14
MIN_OBSERVATIONS = 3

_METRIC_PRIORITY = [
    MetricType.STARS.value,
    MetricType.DOWNLOADS.value,
    MetricType.ENGAGEMENT.value,
    MetricType.FORKS.value,
    MetricType.CITATIONS.value,
    MetricType.MENTIONS.value,
    MetricType.COMMENT_COUNT.value,
]

_HIGH_VALUE_THRESHOLDS: dict[str, float] = {
    MetricType.STARS.value: 1000.0,
    MetricType.DOWNLOADS.value: 100_000.0,
    MetricType.ENGAGEMENT.value: 100.0,
    MetricType.FORKS.value: 200.0,
    MetricType.COMMENT_COUNT.value: 50.0,
}


class SignalDetector:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _pick_metric(self, entity_id: str) -> str | None:
        for metric in _METRIC_PRIORITY:
            obs = self.db.get_observations(entity_id, metric, limit=3)
            if obs:
                return metric
        return None

    def detect_for_entity(self, entity: Entity) -> Signal | None:
        metric = self._pick_metric(entity.id)
        if not metric:
            return None

        observations = self.db.get_observations(entity.id, metric, limit=90)

        if len(observations) < MIN_OBSERVATIONS:
            if len(observations) == 1:
                return self._bootstrap_signal(entity, observations[0], metric)
            return None

        values = [o.metric_value for o in observations]
        velocity = compute_velocity(values)
        acceleration = compute_acceleration(values)
        z = compute_rolling_z_score(values, window=WINDOW)

        if abs(z) < Z_THRESHOLD:
            return None

        signal_type = SignalType.GROWTH_SURGE if z > 0 else SignalType.ANOMALY
        confidence = min(0.99, abs(z) / 10.0)
        summary = (
            f"{entity.name} shows {metric} Z-score {z:+.2f} "
            f"(v={velocity:+.1f}/period, a={acceleration:+.2f})"
        )

        return Signal(
            entity_id=entity.id,
            entity_name=entity.name,
            entity_type=entity.entity_type,
            signal_type=signal_type,
            z_score=round(z, 4),
            velocity=round(velocity, 4),
            acceleration=round(acceleration, 4),
            confidence=round(confidence, 4),
            summary=summary,
        )

    def _bootstrap_signal(
        self, entity: Entity, obs: Observation, metric: str
    ) -> Signal | None:
        threshold = _HIGH_VALUE_THRESHOLDS.get(metric, 50.0)
        value = obs.metric_value
        if value < threshold:
            return None
        z = min(10.0, (value / threshold) * 2.5)
        return Signal(
            entity_id=entity.id,
            entity_name=entity.name,
            entity_type=entity.entity_type,
            signal_type=SignalType.GROWTH_SURGE,
            z_score=round(z, 4),
            velocity=0.0,
            acceleration=0.0,
            confidence=0.5,
            summary=(
                f"{entity.name}: {metric} = {value:.0f} "
                f"exceeds baseline threshold of {threshold:.0f}"
            ),
        )


def compute_velocity(values: list[float]) -> float:
    """Average daily delta over last 7 observations."""
    if len(values) < 2:
        return 0.0
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    window = deltas[-7:]
    return sum(window) / len(window)


def compute_acceleration(values: list[float]) -> float:
    """Second-order difference — rate of change of velocity."""
    if len(values) < 3:
        return 0.0
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    if len(deltas) < 2:
        return 0.0
    accel = [deltas[i] - deltas[i - 1] for i in range(1, len(deltas))]
    window = accel[-6:]
    return sum(window) / len(window)


def compute_rolling_z_score(values: list[float], window: int = 14) -> float:
    """Z-score of latest value relative to rolling baseline window."""
    if len(values) < 3:
        return 0.0
    baseline = values[:-1]
    baseline_window = baseline[-window:]
    if len(baseline_window) < 2:
        return 0.0
    mu = statistics.mean(baseline_window)
    sigma = statistics.stdev(baseline_window)
    diff = values[-1] - mu
    if abs(diff) < 1e-9:
        return 0.0
    if sigma < 1e-9:
        scale = max(abs(mu) * 0.1, 1.0)
        return diff / scale
    return diff / sigma
