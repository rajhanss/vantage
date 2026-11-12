# VANTAGE — Agentic Research & Investigation Architecture

## 1. Overview

Vantage features an autonomous multi-agent research framework designed to investigate signals detected by the quantitative engine. Rather than simply alerting the user that a metric changed, the Agentic Research Subsystem investigates *why* it changed, *who* is driving it, *how* it connects to historical developments, and *what* experts or communities are saying.

---

## 2. Specialized Logical Agent Roles

The multi-agent system uses specialized functional agents operating under a central **Investigation Orchestrator**:

```
                       ┌───────────────────────────────┐
                       │   Investigation Orchestrator  │
                       │     (State & Goal Planner)    │
                       └──────────────┬────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  Evidence Agent  │        │   Entity Agent   │        │  Temporal Agent  │
│ - Source Verify  │        │ - Knowledge Graph│        │ - Curve Fitting  │
│ - Contradictions │        │ - Aliases & Orgs │        │ - Velocity Shift │
└──────────────────┘        └──────────────────┘        └──────────────────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      ▼
                       ┌───────────────────────────────┐
                       │        Synthesis Agent        │
                       │  - Evidence-Backed Dossier    │
                       │  - Calibrated Confidence      │
                       └───────────────────────────────┘
```

### 2.1 Investigation Orchestrator
- Receives an investigation trigger (either an automated anomaly signal from the quantitative engine or a user question).
- Formulates hypothesis trees and decomposes research objectives into parallel tasks.
- Manages state, prevents loop stalls, and enforces deadline timeouts.

### 2.2 Evidence Agent
- Searches external and internal indexes for primary sources.
- Checks source authority, publication dates, and cross-source corroboration.
- Explicitly flags unsupported claims or contradictory assertions across sources.

### 2.3 Entity & Graph Agent
- Discovers named entities (authors, libraries, companies, communities).
- Queries the entity relationship graph to detect community clusters, co-occurrence patterns, and influence paths.

### 2.4 Temporal Intelligence Agent
- Inspects historical time-series data for the topic or entity.
- Fits growth curves (exponential, logistic, declining) and identifies structural change-points.

### 2.5 Synthesis Agent
- Compiles findings into an executive intelligence report.
- Cites every factual assertion with exact URLs, dates, and evidence IDs.
- Outputs structured intelligence reports with confidence scores.

---

## 3. Investigation Lifecycle & State Machine

1. **Trigger & Goal Definition**: Anomaly detected (e.g., star velocity $Z > 3.5$) $\rightarrow$ Objective defined.
2. **Context Retrieval**: Retrieve entity profile, historical metrics, and related graph nodes.
3. **Multi-Source Evidence Gathering**: Fetch recent releases, HN discussions, arXiv preprints, and commit logs.
4. **Cross-Validation**: Filter hallucinations, reconcile timestamp ordering, and identify counter-evidence.
5. **Report Generation**: Produce markdown intelligence dossier with quantitative charts and timeline.
6. **Persistence**: Store investigation dossier, update entity graph, and schedule recurring monitoring.

---

## 4. Guardrails & Safety Mandates

1. **Anti-Hallucination Barrier**: Agents are strictly prohibited from generating synthetic statistics, fake paper titles, or phantom URLs. If an adapter returns no data, the agent must explicitly state `Insufficient Evidence`.
2. **Context Isolation**: External web pages and discussion threads are sanitized and passed as untrusted data blocks. System prompt instructions can never be overridden by retrieved content.
3. **Deterministic Pre-flight**: Quantitative data (star count, commit velocity, download numbers) is provided to agents from validated SQLite / PostgreSQL tables, not guessed by the model.
