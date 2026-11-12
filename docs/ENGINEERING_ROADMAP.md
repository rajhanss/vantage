# VANTAGE — Engineering Roadmap & Milestones

---

### Milestone 1: Core Foundation & Data Acquisition Subsystem
- [x] Monorepo layout (`backend/`, `web/`, `docs/`).
- [x] Pydantic v2 domain schemas (`Entity`, `Observation`, `Signal`, `Investigation`, `Relationship`).
- [x] Modular Data Source Adapters:
  - GitHub Trending & Releases Adapter
  - Hugging Face Model Trends Adapter
  - PyPI / Package Velocity Adapter
  - HackerNews Developer Discussions Adapter
  - arXiv Research Preprint Adapter
- [x] Ingestion runner with deduplication and sqlite/postgres persistence.

### Milestone 2: Algorithmic Intelligence Engine
- [x] Signal Engine: Rolling Z-scores, velocity, acceleration, CUSUM drift detection.
- [x] Temporal Modeler: Logistic curve fitting, adoption lifecycle classification, momentum scoring.
- [x] Graph Subsystem: Entity co-occurrence graph, degree & betweenness centrality, community clusters.

### Milestone 3: Predictive & Recommendation Engines
- [x] Forecasting Engine: Damped exponential smoothing with 80% and 95% calibrated confidence intervals.
- [x] Two-Tower Recommendation Engine: Profile decay weighting, candidate retrieval, diversity re-ranking.

### Milestone 4: Multi-Agent Research & Investigation Workspace
- [x] Investigation Orchestrator: State machine for signal decomposition.
- [x] Evidence & Entity Agents: Cross-checking source reliability, citation anchoring.
- [x] Synthesis Agent: Generating structured markdown intelligence dossiers with verified facts.

### Milestone 5: Web Intelligence Terminal (React 18 + TypeScript + Vite)
- [x] High-density dark-mode intelligence dashboard.
- [x] Live Signal Ticker & Anomaly Radar.
- [x] Interactive Trend Trajectory Charts with confidence interval bands.
- [x] Knowledge Graph Explorer with community clustering.
- [x] On-Demand Investigation Dossier Viewer.

### Milestone 6: Automated Testing & Cloud Deployment
- [x] Unit test suites for math, signal detection, graph, forecasting, adapters, and API routes.
- [x] Production Dockerfile & Render.com deployment Blueprint (`render.yaml`).
- [x] Complete end-to-end operational verification.
