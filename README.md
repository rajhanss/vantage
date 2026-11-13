# Vantage

**Adversarial Testing and Security Assessment Framework for Autonomous AI Agents**

Vantage is an open security assessment harness that stress-tests autonomous AI agents against the [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/) (ASI01–ASI10). It fires deterministic adversarial scenarios at any agent, records what happens through instrumented canary conditions, and produces scored reports that show exactly where an agent fails.

---

## What it does

| Capability | Detail |
|------------|--------|
| **10 attack categories** | ASI01 Goal Hijacking through ASI10 Rogue Agent Drift |
| **Deterministic oracle** | No LLM judge — canary conditions are evaluated against recorded tool calls and state changes |
| **Wilson score intervals** | Attack Success Rate (ASR) reported with 95% confidence bounds, not point estimates |
| **Multiple target adapters** | In-process, HTTP (REST), and subprocess targets |
| **Reference testbed** | `ToyAgentTarget` ships with vulnerable and hardened modes for calibration |
| **Report formats** | JSON, Markdown, HTML — all with secret redaction |
| **Run comparison** | Defense efficacy delta across two assessment runs |
| **React dashboard** | Live assessment progress, OWASP heatmap, scenario catalog, and run comparison |

---

## Architecture

```
vantage/
├── scenarios/          YAML adversarial scenario definitions (ASI01–ASI10)
├── engine/             Async trial execution engine with event bus
├── oracle/             Deterministic canary condition evaluator
├── scoring/            Wilson interval calculator and risk grade aggregator
├── targets/            Target adapters (in-process, HTTP, subprocess)
├── testbed/            ToyAgentTarget reference implementation
├── report/             JSON / Markdown / HTML report generators
├── api/                FastAPI routes (scenarios, runs, reports, compare)
└── data/storage/       SQLite persistence for runs and reports
```

---

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for the dashboard)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn vantage.main:app --reload
```

### Frontend

```bash
cd web
npm install
npm run dev
```

The API runs at `http://localhost:8000`. The dashboard connects automatically.

---

## Running assessments

### Against the built-in testbed

```bash
# Launch an assessment via the dashboard at http://localhost:5173
# Or via the API:

curl -X POST http://localhost:8000/api/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "target": {"kind": "inprocess", "module": "vantage.testbed.toy_agent", "class_name": "ToyAgentTarget", "init_kwargs": {"mode": "vulnerable"}},
    "scenario_ids": null,
    "trials_per_scenario": 3,
    "timeout_seconds": 30
  }'
```

### Against an HTTP agent

```bash
curl -X POST http://localhost:8000/api/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "target": {"kind": "http", "base_url": "https://your-agent.example.com"},
    "scenario_ids": null,
    "trials_per_scenario": 5,
    "timeout_seconds": 60
  }'
```

---

## Test suite

```bash
cd backend
pytest tests -v
# 50 passed
```

---

## OWASP categories covered

| ID | Name |
|----|------|
| ASI01 | Goal and Instruction Hijacking |
| ASI02 | Tool and Resource Misuse |
| ASI03 | Privilege and Authorization Escalation |
| ASI04 | Poisoned Tool Descriptions |
| ASI05 | Unexpected Remote Code Execution |
| ASI06 | Memory Poisoning |
| ASI07 | Message and Identity Spoofing |
| ASI08 | Cascading and Amplification Failures |
| ASI09 | Approval Fatigue |
| ASI10 | Rogue Agent Drift |

---

## License

MIT
