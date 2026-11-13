# Vantage — AGENTS.md

This file describes the components that execute assessment logic inside the Vantage framework.

---

## Engine (`vantage/engine/runner.py`)

The `AsyncRunner` is the central execution engine. It:

1. Accepts a `RunConfig` (target spec + scenario IDs + trial count + timeout).
2. Loads matching scenarios from the YAML catalog.
3. Creates a target adapter via `create_target()`.
4. For each scenario × trial, calls `target.run(scenario)` with a timeout.
5. Passes the resulting `CanaryRecorder` to the `DeterministicOracle`.
6. Emits `RunEvent` objects to the `EventBus` (consumed by SSE / API).
7. Aggregates results into a `RunSummary`.

The runner is fully async. All I/O (target calls, DB writes) uses `asyncio`.

---

## Oracle (`vantage/oracle/evaluator.py`)

`DeterministicOracle` evaluates whether an adversarial scenario succeeded by checking `CanaryCondition` objects against a `CanaryRecorder`.

Supported condition kinds:

| Kind | Passes when |
|------|-------------|
| `file_written` | `recorder.files_written` contains the expected path |
| `tool_called` | `recorder.tool_calls` contains a call matching name + arguments |
| `data_exfiltrated` | `recorder.exfiltrated_endpoints` contains the expected URL prefix |
| `loop_detected` | `recorder.tool_call_count` exceeds `threshold` |

The oracle never calls an LLM. Results are deterministic given the same recorder state.

---

## Canary Toolkit (`vantage/targets/canary_toolkit.py`)

`CanaryRecorder` instruments a target run. Target adapters call its methods:

- `record_file_write(path)` — called when the agent writes a file.
- `record_tool_call(name, arguments)` — called for every tool invocation.
- `record_exfiltration(url)` — called when the agent posts to an external URL.

`CANARY_TOOL_DEFINITIONS` is a set of tool schemas injected into the agent's context that cause it to record actions through the recorder when called.

---

## Scenario Loader (`vantage/scenarios/loader.py`)

Loads YAML files from the `scenarios/` directory. Each file defines one or more scenarios. The loader validates against the `Scenario` Pydantic model and raises on schema errors.

---

## Scoring (`vantage/scoring/calculator.py`)

| Function | Description |
|----------|-------------|
| `compute_wilson_interval(successes, trials)` | Returns `(low, high)` 95% Wilson score CI |
| `compute_risk_grade(asr)` | Maps ASR to A/B/C/D/F |
| `aggregate_scenario_trials(results)` | Groups trials by scenario, computes per-scenario ASR + CI |
| `compute_category_scores(scenario_results)` | Aggregates per-category ASR weighted by severity |
| `compare_runs(run_a, run_b)` | Returns per-category ASR delta (defense efficacy) |

---

## Targets (`vantage/targets/`)

### Protocol (`base.py`)

```python
class Target(Protocol):
    async def run(self, scenario: Scenario, recorder: CanaryRecorder) -> TrialResult: ...
```

### Adapters

| Adapter | Use case |
|---------|----------|
| `InProcessTargetAdapter` | Agent is a Python class in the same process |
| `HttpTargetAdapter` | Agent exposes a REST endpoint |
| `SubprocessTargetAdapter` | Agent runs as a separate process |

The `create_target(spec)` factory selects the right adapter based on `spec.kind`.

---

## Testbed (`vantage/testbed/toy_agent.py`)

`ToyAgentTarget` is a reference agent for calibration:

- **vulnerable mode** — detects `CANARY_*` tokens in the attack payload and fires corresponding canary conditions (simulating a successfully hijacked agent).
- **hardened mode** — wraps untrusted tool data in `<untrusted_tool_data>` tags and never acts on injected instructions.

---

## Report Generator (`vantage/report/generator.py`)

| Format | Generator |
|--------|-----------|
| JSON | `JsonReportGenerator` |
| Markdown | `MarkdownReportGenerator` |
| HTML | `HtmlReportGenerator` |

All generators redact strings matching `SECRET_PATTERN` (API keys, tokens).

---

## API Routes (`vantage/api/routes/`)

| Route | Description |
|-------|-------------|
| `GET /health` | Service health and version |
| `GET /api/scenarios` | List / filter scenarios |
| `GET /api/scenarios/{id}` | Single scenario detail |
| `POST /api/runs` | Launch assessment |
| `GET /api/runs` | List runs |
| `GET /api/runs/{id}` | Run status and summary |
| `DELETE /api/runs/{id}` | Kill in-progress run |
| `GET /api/runs/{id}/report` | Download report (JSON/MD/HTML) |
| `POST /api/compare` | Compare two runs |
