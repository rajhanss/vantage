"""YAML scenario loader and validator for Vantage."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence
import yaml

from vantage.models.domain import AttackStep, CanaryCondition, OwaspCategory, Scenario, Severity, StepType


def load_scenarios_from_yaml(file_path: Path) -> list[Scenario]:
    """Parse and validate scenarios from a YAML file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Scenario pack not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or not isinstance(data, dict):
        return []

    pack_category_str = data.get("category", "")
    pack_category = OwaspCategory(pack_category_str) if pack_category_str else None

    raw_scenarios = data.get("scenarios", [])
    scenarios: list[Scenario] = []

    for raw in raw_scenarios:
        cat_str = raw.get("category", pack_category_str)
        cat = OwaspCategory(cat_str)

        steps: list[AttackStep] = []
        for step in raw.get("attack_steps", []):
            steps.append(
                AttackStep(
                    step_id=step["step_id"],
                    step_type=StepType(step["step_type"]),
                    content=step["content"],
                    tool_name=step.get("tool_name"),
                    call_id=step.get("call_id"),
                    metadata=step.get("metadata", {}),
                )
            )

        canaries: list[CanaryCondition] = []
        for can in raw.get("canaries", []):
            canaries.append(CanaryCondition.model_validate(can))

        scenario = Scenario(
            id=raw["id"],
            name=raw["name"],
            category=cat,
            severity=Severity(raw.get("severity", "HIGH")),
            description=raw.get("description", ""),
            setup=raw.get("setup", {}),
            attack_steps=steps,
            canaries=canaries,
            remediation_hint=raw.get("remediation_hint", ""),
            tags=raw.get("tags", []),
        )
        scenarios.append(scenario)

    return scenarios


def load_all_scenarios(scenarios_dir: Path | None = None) -> list[Scenario]:
    """Load all scenario packs from the scenarios directory."""
    dir_path = scenarios_dir or Path(__file__).parent
    all_scenarios: list[Scenario] = []

    for file_path in sorted(dir_path.glob("asi*.yaml")):
        all_scenarios.extend(load_scenarios_from_yaml(file_path))

    return all_scenarios
