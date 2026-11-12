# VANTAGE — System Architecture Specification

## 1. High-Level Architecture Overview

Vantage is architected as a modular, unified intelligence platform comprising five decoupled layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION TIER (UI)                          │
│     React 18 + TypeScript + Vite + TailwindCSS + Lucide + Recharts     │
│   Intelligence Terminal • Signal Explorer • Investigation Workspace    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / WebSocket (FastAPI)
┌───────────────────────────────────▼────────────────────────────────────┐
│                         APPLICATION API TIER                           │
│  FastAPI • REST v1 • WebSocket Subscriptions • OpenAPI Documentation   │
│  Auth Middleware • Rate Limiting • Job Dispatch • Telemetry Tracing    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                       INTELLIGENCE CORE ENGINES                        │
│ ┌───────────────────┐ ┌───────────────────┐ ┌────────────────────────┐ │
│ │ Signal Detection  │ │ Temporal Modeler  │ │ Graph Intelligence     │ │
│ │ (Z-Score, CUSUM)  │ │ (Logistic, Decay) │ │ (NetworkX / Co-occur)  │ │
│ └───────────────────┘ └───────────────────┘ └────────────────────────┘ │
│ ┌───────────────────┐ ┌───────────────────┐ ┌────────────────────────┐ │
│ │ Recommendation    │ │ Multi-Agent Intel │ │ Predictive Engine      │ │
│ │ (Two-Tower / Cos) │ │ (LangGraph Core)  │ │ (Time-series Forecast) │ │
│ └───────────────────┘ └───────────────────┘ └────────────────────────┘ │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    DATA ACQUISITION & INGESTION                        │
│  Modular Source Adapters: GitHub API • HuggingFace • PyPI • arXiv • HN  │
│  Rate-Limiter • Deduplication Buffer • Normalization • Schema Validator │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         PERSISTENCE & STORAGE                          │
│  SQLite / Supabase Postgres (Entities, Observations, Signals, Dossiers)│
│  In-Memory / Qdrant-Compatible Vector Embeddings (MiniLM / CLIP)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Organization

```
Vantage/
├── backend/
│   ├── vantage/
│   │   ├── api/             # FastAPI routes (/signals, /trends, /entities, /investigate)
│   │   ├── core/            # Configuration, logging, exception handlers
│   │   ├── intelligence/    # Algorithmic and ML intelligence engines
│   │   │   ├── signals/     # Anomaly, Z-score, burst detection
│   │   │   ├── temporal/    # Growth curve fitting, velocity, acceleration
│   │   │   ├── graph/       # Co-occurrence, network clustering, community metrics
│   │   │   ├── ranking/     # Recommendation engine (candidate retrieval, ranking)
│   │   │   ├── forecasting/ # Exponential smoothing, linear trends, calibrated CI
│   │   │   └── agents/      # Multi-agent investigation orchestrator & synthesizers
│   │   ├── data/            # Data ingestion, adapters, normalization
│   │   │   ├── adapters/    # GitHub, Hugging Face, PyPI, arXiv, HackerNews
│   │   │   ├── pipelines/   # Ingestion runner, scheduled tasks
│   │   │   └── storage/     # SQLite / Postgres repository layer
│   │   └── models/          # Pydantic domain models & schemas
│   ├── tests/               # Unit, integration, and algorithmic tests
│   ├── pyproject.toml
│   └── Dockerfile
├── web/                     # React 18 + Vite Intelligence Terminal
│   ├── src/
│   │   ├── components/      # Terminal cards, charts, graph visualizers, signals
│   │   ├── pages/           # Dashboard, TrendDetail, Investigation, EntityMap
│   │   ├── api/             # Typed API client
│   │   └── types/           # Shared interface definitions
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Architectural blueprints and engineering specs
├── render.yaml              # Cloud deployment specification
├── DEPLOY_AND_RUN.md        # One-click execution and validation guide
└── README.md
```

---

## 3. Technology Stack Justification

| Layer | Selected Tech | Rationale |
|---|---|---|
| **Backend Framework** | Python 3.12 + FastAPI | Native async performance, Pydantic v2 validation, standard for AI/ML pipelines. |
| **Statistical & ML Core** | NumPy, SciPy, scikit-learn | Fast vectorized baseline computation for signal detection, anomaly scoring, and trend fitting without massive GPU overhead. |
| **Graph Analysis** | NetworkX | In-memory graph analytics (betweenness, degree centrality, modularity communities) perfectly suited for developer entity networks. |
| **Agent Orchestrator** | Custom Lightweight State Machine / LangGraph pattern | Deterministic state transitions, parallel tool calling, structured JSON output enforcement. |
| **Storage** | SQLite (local) + Supabase PostgreSQL (cloud) | Zero operational friction locally with seamless production upgrade to cloud Postgres with pgvector. |
| **Frontend** | React 18 + TypeScript + Vite + TailwindCSS | Fast, responsive desktop intelligence terminal layout with dark-mode aesthetic, micro-animations, and interactive data visualization. |
| **Visualization** | Recharts + SVG Graph Visualizers | Crisp temporal line graphs, radar metrics, and interactive network force diagrams. |
