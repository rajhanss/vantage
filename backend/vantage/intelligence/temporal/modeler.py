"""Temporal lifecycle modeling, momentum scoring, and curve fitting."""
from __future__ import annotations

import math

from vantage.models.domain import LifecycleStage


def classify_lifecycle_stage(
    velocity: float,
    acceleration: float,
    z_score: float,
) -> LifecycleStage:
    """
    Map (velocity, acceleration, z_score) → LifecycleStage.

    Decision logic mirrors product adoption S-curve phases:
      ACCELERATION  — fast-growing, still accelerating, strong signal
      INFLECTION    — positive velocity, decelerating (peak/plateau approaching)
      SATURATION    — slowing but positive velocity
      DECAY         — negative velocity
      EMERGENCE     — default / early weak signal
    """
    if velocity > 0 and acceleration > 0 and z_score >= 2.0:
        return LifecycleStage.ACCELERATION
    if velocity > 0 and z_score >= 1.0:
        if acceleration >= 0:
            return LifecycleStage.INFLECTION
        return LifecycleStage.SATURATION
    if velocity < 0:
        return LifecycleStage.DECAY
    return LifecycleStage.EMERGENCE


def compute_momentum_score(
    velocity: float,
    z_score: float,
    acceleration: float,
) -> float:
    """
    Composite momentum score in [0.0, 1.0].

    Components:
      - Z-score contribution (40%) — statistical signal strength
      - Velocity contribution  (40%) — absolute growth rate (log-scaled)
      - Acceleration bonus     (20%) — trend direction
    """

    def _sigmoid(x: float, scale: float = 1.0) -> float:
        return 1.0 / (1.0 + math.exp(-x / scale))

    z_component = _sigmoid(z_score, scale=4.0)
    vel_component = _sigmoid(math.log1p(abs(velocity)) * math.copysign(1, velocity), scale=2.0)
    accel_component = _sigmoid(acceleration, scale=5.0)

    raw = 0.40 * z_component + 0.40 * vel_component + 0.20 * accel_component
    return max(0.0, min(1.0, raw))


def fit_logistic_curve(
    times: list[float],
    values: list[float],
) -> dict:
    """
    Fit a logistic adoption curve: f(t) = L / (1 + exp(-k*(t - t0))).
    Returns fitted parameters or {'fitted': False} on failure.
    """
    if len(times) < 4 or len(values) < 4:
        return {"L": 0.0, "k": 0.0, "t0": 0.0, "fitted": False}

    try:
        import numpy as np
        from scipy.optimize import curve_fit

        t = np.array(times, dtype=float)
        v = np.array(values, dtype=float)

        # Normalize time to [0, 1] for numerical stability
        t_min, t_range = t.min(), t.ptp()
        t_norm = (t - t_min) / (t_range + 1e-9)

        v_max = float(v.max())

        def logistic(t: "np.ndarray", L: float, k: float, t0: float) -> "np.ndarray":
            return L / (1.0 + np.exp(-k * (t - t0)))

        popt, _ = curve_fit(
            logistic,
            t_norm,
            v,
            p0=[v_max * 1.2, 3.0, 0.5],
            bounds=([0, 0.01, -1], [v_max * 10, 50, 2]),
            maxfev=8000,
        )
        return {
            "L": float(popt[0]),
            "k": float(popt[1]),
            "t0": float(popt[2]),
            "fitted": True,
        }
    except Exception:
        return {"L": 0.0, "k": 0.0, "t0": 0.0, "fitted": False}
