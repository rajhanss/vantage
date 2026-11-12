# VANTAGE — Multimodal Temporal Intelligence Platform

[![Build & Test](https://img.shields.io/badge/tests-79%20passed%20%7C%20100%25-brightgreen.svg)](https://github.com/rajhanss/vantage)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178c6.svg)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5.4-646cff.svg)](https://vitejs.dev)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> *"See Beyond the Obvious."*
>
> An intelligence terminal for the internet's emerging trends, communities, ideas, models, and digital ecosystems.

---

## 1. Product Overview

The digital ecosystem continuously produces signals — GitHub repositories exploding overnight, HuggingFace models overtaking benchmarks, arXiv papers introducing new paradigms, PyPI packages gaining exponential adoption, and HackerNews discussions signaling cultural and technical inflection points.

Most of this intelligence remains fragmented across platforms. **Vantage** connects these fragments, detects meaningful statistical signals, reconstructs adoption curves, investigates underlying catalysts, and forecasts 30-day trajectories with empirical prediction intervals.

```
Information → Signals → Patterns → Context → Intelligence → Predictions → Decisions
```

---

## 2. Intelligence Architecture

Vantage is built on a clean three-tier intelligence substrate:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             VANTAGE TERMINAL                                │
│          React 18 + TypeScript + Vite + TailwindCSS + Recharts               │
│  [Radar Signals]   [30d Trajectories]   [Graph Matrix]   [AI Dossiers]      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ REST API (FastAPI)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                        ANALYTICAL INTELLIGENCE CORE                         │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │    Signal Detector    │  │    Temporal Modeler   │  │  Holt-Winters   │  │
│  │   Z-Score / Velocity  │  │   S-Curve Lifecycle   │  │  30d Forecast   │  │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘  │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │   Topological Graph   │  │   Two-Tower Recommender│ │ Agent Dossiers   │  │
│  │  Louvain Modularity   │  │   Cosine + MMR Ranker │  │ Groq Llama-3/Qwen│ │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                          MODULAR SOURCE ADAPTERS                            │
│  [GitHub Search]  [HuggingFace Hub]  [arXiv Atom]  [HackerNews]  [PyPI JSON] │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Subsystems

1. **Statistical Signal Detection (`vantage.intelligence.signals`)**
   - Rolling Z-score anomaly detector across $\ge 2.5\sigma$ deviations.
   - 1st-order finite difference velocity ($v = \Delta y / \Delta t$) over 7-day smoothing windows.
   - 2nd-order acceleration ($a = \Delta^2 y / \Delta t^2$) to detect inflection before saturation.
   - Cold-start bootstrap estimators for high-impact single-observation arrivals.

2. **Temporal S-Curve Modeling (`vantage.intelligence.temporal`)**
   - Mathematical classification across 5 lifecycle stages:
     - **Emergence:** Weak initial signal, early co-occurrence.
     - **Acceleration:** $v > 0, a > 0, Z \ge 2.0\sigma$ — exponential takeoff.
     - **Inflection:** Peak velocity, deceleration beginning ($a \le 0$).
     - **Saturation:** High volume, decaying velocity ($v \to 0$).
     - **Decay:** Negative velocity ($v < 0$).
   - Multi-component composite momentum score bounded strictly in $[0, 1]$.
   - SciPy logistic adoption curve regression ($L / (1 + e^{-k(t - t_0)})$).

3. **30-Day Predictive Forecasting (`vantage.intelligence.forecasting`)**
   - Additive Holt-Winters smoothing with damped trend parameter ($\phi = 0.95$).
   - Non-parametric prediction interval bands (80% and 95%) computed from empirical rolling backtest residual quantiles.
   - Monotonic interval guarantees ($0 \le \text{lower}_{95} \le \text{lower}_{80} \le \hat{y} \le \text{upper}_{80} \le \text{upper}_{95}$).

4. **Network Matrix & Graph Intelligence (`vantage.intelligence.graph`)**
   - Co-occurrence graph constructed across cross-platform entity mentions.
   - Greedy modularity community clustering (Louvain).
   - Degree centrality, normalized betweenness centrality, and PageRank.

5. **Two-Tower Semantic Recommender (`vantage.intelligence.ranking`)**
   - Hand-crafted categorical + metric feature projection vectors.
   - Cosine similarity matching in continuous feature space.
   - Maximal Marginal Relevance (MMR) re-ranking ($\lambda = 0.70$) to prevent filter bubbles and guarantee diversity.

6. **Multi-Agent Deep Investigation (`vantage.intelligence.agents`)**
   - Structured investigation dossier synthesizer.
   - Groq LLaMA-3 / Qwen integration with automatic prompt isolation (`<untrusted>` content tags).
   - Deterministic rule-based analytical synthesizer fallback when API keys are unconfigured.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Runtime** | Python 3.12, FastAPI, Pydantic v2, Uvicorn |
| **Statistical & ML Math** | NumPy, SciPy (`curve_fit`), NetworkX |
| **Data & Storage** | SQLite (WAL mode, foreign keys, thread-safe repository) |
| **Frontend Terminal** | React 18, TypeScript 5.6, Vite 5.4, TailwindCSS, Recharts, Lucide Icons |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX TestClient (79 automated tests) |
| **Deployment** | Docker multi-stage container, Render.com blueprint |

---

## 4. Quick Start (Local Execution)

### Prerequisites
- Python 3.11+
- Node.js 18+ (optional if using prebuilt static frontend)

### 1. Clone & Set Up Backend

```bash
git clone https://github.com/rajhanss/vantage.git
cd vantage/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Run Test Suite

```bash
python -m pytest tests -v
# Output: 79 passed in ~2s (100% pass rate)
```

### 3. Build Web Frontend

```bash
cd ../web
npm install
npm run build

# Copy build to backend static directory
cp -r dist ../backend/vantage/static
```

### 4. Start the Terminal

```bash
cd ../backend
uvicorn vantage.main:app --host 0.0.0.0 --port 8000 --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser. The API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 5. API Reference

All REST endpoints are documented with OpenAPI schemas:

- `GET /health` — Service health probe and version
- `GET /api/v1/stats` — Platform counts across entities, observations, signals, and investigations
- `GET /api/v1/signals` — Real-time detected anomalies and velocity surges (supports `min_z_score`, `limit`)
- `GET /api/v1/trends` — Ranked trend leaderboard with momentum scores and S-curve stages
- `GET /api/v1/trends/{entity_id}` — Trajectory detail with 30-day Holt-Winters forecast points
- `GET /api/v1/graph` — Co-occurrence network nodes, edges, betweenness, and community clusters
- `GET /api/v1/recommendations?entity_id={id}` — Similar entities ranked via two-tower MMR
- `POST /api/v1/investigate` — Synthesize or retrieve deep investigation dossier for target entity
- `POST /api/v1/ingest/trigger` — Trigger on-demand sweep across public source adapters

---

## 6. Cloud Deployment

### Docker Deployment

```bash
docker build -t vantage:latest .
docker run -p 8000:8000 -e PORT=8000 vantage:latest
```

### Deploy to Render.com

1. Push to GitHub repository.
2. In the Render Dashboard, select **New +** → **Blueprint** and link this repository (`render.yaml`).
3. Set optional environment secrets (`VANTAGE_GROQ_API_KEY`, `VANTAGE_TAVILY_API_KEY`) in the Render Dashboard environment settings.

---

## 7. License

Distributed under the MIT License. See `LICENSE` for details.
