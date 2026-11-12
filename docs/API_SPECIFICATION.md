# VANTAGE — REST & WebSocket API Specification

## 1. Overview
Base URL: `/api/v1`  
OpenAPI Documentation: `/docs` (when debug is enabled)  
All responses use standard JSON with ISO 8601 UTC timestamps.

---

## 2. API Endpoints

### 2.1 Health & System Diagnostics
- `GET /health`
  - Returns `{"status": "healthy", "version": "0.1.0", "timestamp": "..."}`.
- `GET /api/v1/stats`
  - Returns total entities tracked, observation counts, active signals, and source status.

### 2.2 Signals & Anomalies
- `GET /api/v1/signals`
  - Parameters:
    - `limit` (int, default 50)
    - `min_z_score` (float, default 2.0)
    - `signal_type` (string, optional: `growth_surge`, `velocity_spike`, `anomaly`)
  - Returns: List of `Signal` objects with entity details, current velocity, and confidence.

### 2.3 Trends & Temporal Trajectories
- `GET /api/v1/trends`
  - Parameters:
    - `entity_type` (string, optional: `repository`, `model`, `package`, `topic`)
    - `timeframe` (string, default `30d`)
  - Returns: Ranked trending items with velocity, acceleration, and lifecycle stage.
- `GET /api/v1/trends/{entity_id}`
  - Returns: Complete entity dossier including historical observation points, fitted curve parameters, 30-day forecast, and related graph nodes.

### 2.4 Knowledge Graph & Community Network
- `GET /api/v1/graph`
  - Parameters:
    - `min_weight` (float, default 0.1)
    - `max_nodes` (int, default 100)
  - Returns: `{ "nodes": [...], "edges": [...], "communities": [...] }` suitable for force-directed visualization.

### 2.5 Agentic Investigations
- `POST /api/v1/investigate`
  - Body:
    ```json
    {
      "entity_id": "uuid-here",
      "focus_question": "Why did repository velocity surge 300% this week?"
    }
    ```
  - Returns: Generated `InvestigationDossier` containing synthesized findings, cross-checked evidence sources, and confidence score.
- `GET /api/v1/investigations/{id}`
  - Returns cached dossier with cited evidence links.

### 2.6 Recommendations
- `GET /api/v1/recommendations`
  - Parameters: `user_id`, `limit` (default 20)
  - Returns: Personalized candidate items with explainability strings (e.g., *"Recommended due to high velocity in your followed Rust ecosystem"*).

### 2.7 Ingestion Management
- `POST /api/v1/ingest/trigger`
  - Executes on-demand ingestion run across configured source adapters.

---

## 3. WebSocket Streams

- `WS /api/v1/ws/signals`
  - Emits real-time JSON events whenever an anomalous signal is detected or an agent investigation completes.
