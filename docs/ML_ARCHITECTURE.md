# VANTAGE — Machine Learning & Algorithmic Intelligence Architecture

## 1. Quantitative Foundations

Vantage strictly separates deterministic quantitative modeling from generative LLM reasoning. Machine learning and statistical algorithms compute numerical signals, metrics, and forecasts; LLM agents contextualize, explain, and synthesize evidence.

---

## 2. Signal Detection Subsystem

### 2.1 Rolling Z-Score & Velocity
Given a time-series of metric observations $M = [m_1, m_2, \dots, m_T]$:

1. **Velocity ($v_t$)**: First derivative of metric change over observation window $\Delta t$:
   $$v_t = \frac{m_t - m_{t-\Delta t}}{\Delta t}$$

2. **Acceleration ($a_t$)**: Second derivative measuring momentum shifts:
   $$a_t = \frac{v_t - v_{t-\Delta t}}{\Delta t}$$

3. **Rolling Z-Score ($Z_t$)**: Computed against a baseline rolling window of $W$ steps:
   $$\mu_W = \frac{1}{W} \sum_{i=t-W}^{t-1} v_i, \quad \sigma_W = \sqrt{\frac{1}{W} \sum_{i=t-W}^{t-1} (v_i - \mu_W)^2}$$
   $$Z_t = \frac{v_t - \mu_W}{\sigma_W + \epsilon}$$

An alert signal triggers when $|Z_t| \ge 2.5$ with persistence $> 2$ consecutive intervals.

### 2.2 CUSUM (Cumulative Sum Control Chart)
To detect small, sustained drift in developer interest before an explosive spike occurs:
$$S_t^+ = \max(0, S_{t-1}^+ + (v_t - \mu_W - K))$$
$$S_t^- = \max(0, S_{t-1}^- - (v_t - \mu_W + K))$$
where $K = \frac{1}{2}\sigma_W$. A structural change-point is declared when $S_t^+ > H$ where $H = 5\sigma_W$.

---

## 3. Temporal Modeling & Adoption Lifecycle

Every emerging technology or trend follows an adoption trajectory:
1. **Emergence**: High velocity, low absolute mass ($v_t \gg \mu_W$, small $m_t$).
2. **Acceleration**: Exponential growth phase ($a_t > 0, v_t > 0$).
3. **Maturity / Inflection**: Sigmoidal inflection point ($a_t \approx 0$, maximum velocity).
4. **Saturation**: Deceleration towards plateau ($a_t < 0, v_t \to 0$).
5. **Decay / Obsolescence**: Negative velocity ($v_t < 0$).

Vantage fits observed trajectories to a generalized logistic growth model:
$$m(t) = \frac{L}{1 + e^{-k(t - t_0)}} + \text{residual}(t)$$
where $L$ is carrying capacity, $k$ is steepness, and $t_0$ is the sigmoid midpoint.

---

## 4. Graph Intelligence & Community Topology

Entities that frequently co-occur in the same repositories, papers, or discussion threads form an undirected weighted graph $G = (V, E, W)$:

1. **Edge Weights ($W_{ij}$)**: Jaccard similarity of co-occurring contexts:
   $$W_{ij} = \frac{|C_i \cap C_j|}{|C_i \cup C_j|}$$
2. **Degree & Centrality**: Identifies hub technologies that act as ecosystem bridges:
   $$C_B(v) = \sum_{s \ne v \ne t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
3. **Community Detection**: Modularity-maximizing partitioning detects sub-ecosystems (e.g. "Rust WebAssembly", "Local LLM Inference", "Autonomous Agents").

---

## 5. Recommendation Intelligence

A Two-Tower candidate retrieval and ranking pipeline:
- **Entity Representation**: Sparse feature vectors (tags, language, license, velocity score) + Dense semantic embeddings.
- **User Preference Profile**: Rolling decay weights over interacted topics and saved entities:
  $$P_{\text{user}}(t) = \sum_{i=1}^N \mathbf{e}_i \cdot \gamma^{\Delta t_i}$$
- **Candidate Scoring**:
  $$\text{Score}(u, e) = \cos(P_u, \mathbf{e}) \times (1 + \alpha Z_e) \times \text{DiversityPenalty}$$
  where $Z_e$ rewards emerging velocity and DiversityPenalty prevents topic repetition.

---

## 6. Predictive Intelligence & Calibrated Uncertainty

Forecasting produces a 30-day forward trajectory with 80% and 95% confidence intervals:
- **Model**: Damped trend exponential smoothing + autoregressive velocity terms.
- **Uncertainty Calibration**: Quantile residuals evaluated against rolling historical backtests.
- **Output Schema**:
  ```json
  {
    "horizon_days": 30,
    "forecast_values": [1240, 1310, 1395, ...],
    "lower_bound_80": [1180, 1220, 1280, ...],
    "upper_bound_80": [1300, 1400, 1510, ...],
    "model_type": "damped_holt_winters",
    "mape_historical": 0.064
  }
  ```
