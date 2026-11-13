"""Factory function creating Target instances based on TargetSpec."""
from __future__ import annotations

from vantage.models.domain import TargetSpec, TargetType
from vantage.targets.adapters.http_adapter import HttpTargetAdapter
from vantage.targets.adapters.inprocess import InProcessTargetAdapter
from vantage.targets.adapters.subprocess_adapter import SubprocessTargetAdapter
from vantage.targets.base import Target
from vantage.targets.canary_toolkit import CanaryRecorder


def create_target(spec: TargetSpec, recorder: CanaryRecorder | None = None) -> Target:
    """Instantiate a Target adapter matching the requested spec."""
    if spec.type == TargetType.IN_PROCESS:
        return InProcessTargetAdapter(spec, recorder=recorder)
    elif spec.type == TargetType.HTTP:
        return HttpTargetAdapter(spec)
    elif spec.type == TargetType.SUBPROCESS:
        return SubprocessTargetAdapter(spec)
    else:
        # Fallback to in-process testbed
        return InProcessTargetAdapter(spec, recorder=recorder)
