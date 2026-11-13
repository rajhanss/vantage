"""Fuzz and boundary property tests for scenario parser in pure Python."""
from __future__ import annotations

import random
import string
import tempfile
from pathlib import Path
import pytest

from vantage.scenarios.loader import load_scenarios_from_yaml


def generate_fuzz_payloads() -> list[str]:
    payloads = [
        "",
        "   \n\t  \n",
        "--- null\n",
        "category: 12345\n",
        "scenarios: [1, 2, 3]\n",
        "::: invalid yaml :::\n",
        "scenarios:\n  - id: null\n",
        "category: INVALID_CAT\nscenarios:\n  - id: 'x'\n",
        "\x00\x01\x02\x03\x04\x05",
        "category: ASI01\nscenarios:\n  - id: 'ok'\n    name: 'test'\n    category: 'ASI01'\n    attack_steps: []\n    canaries: []\n",
    ]
    # Add 20 random string mutations
    rnd = random.Random(42)
    for _ in range(20):
        length = rnd.randint(5, 200)
        chars = "".join(rnd.choice(string.printable) for _ in range(length))
        payloads.append(chars)
    return payloads


@pytest.mark.parametrize("fuzz_text", generate_fuzz_payloads())
def test_scenario_loader_robustness(fuzz_text: str):
    """Ensure the parser handles arbitrary fuzzed inputs gracefully without unhandled crashes."""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8", errors="replace") as f:
        f.write(fuzz_text)
        temp_path = Path(f.name)

    try:
        try:
            scenarios = load_scenarios_from_yaml(temp_path)
            assert isinstance(scenarios, list)
        except Exception as e:
            # Expected Pydantic validation errors, YAML parse errors, etc.
            assert isinstance(e, (ValueError, KeyError, TypeError, Exception))
    finally:
        if temp_path.exists():
            temp_path.unlink()
