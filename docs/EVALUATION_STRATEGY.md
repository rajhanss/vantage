# VANTAGE — Evaluation Strategy & Quality Assurance

## 1. Evaluation Philosophy

Vantage treats intelligence systems as empirical software components. No model, heuristic, or agent workflow is trusted without reproducible metrics against defined baselines.

---

## 2. Evaluation Dimensions & Metrics

| Subsystem | Evaluation Task | Metrics | Benchmark / Baseline |
|---|---|---|---|
| **Signal Detection** | Anomaly & Burst Classification | Precision, Recall, FPR, F1-Score | Moving Average Z-score vs Ground Truth surges |
| **Temporal Modeling** | 30-Day Metric Forecasting | MAE, RMSE, SMAPE, Coverage at 80% CI | Naive Persistence ($\hat{y}_{t+h} = y_t$) & Linear Extrapolation |
| **Graph Intelligence** | Community Detection Quality | Modularity ($Q$), Conductance | Random partitioning & Louvain baseline |
| **Recommendation** | Entity Discovery Ranking | Precision@10, Recall@10, NDCG@10, Intra-List Diversity | Popularity-only ranking baseline |
| **Agentic Research** | Evidence Verification & Synthesis | Citation Validity Rate ($> 95\%$), Unsupported Assertion Rate ($< 5\%$) | Human-labeled benchmark dossiers |

---

## 3. Time-Aware Cross Validation

To eliminate future temporal leakage:
- Evaluators strictly use **rolling origin backtesting** (train on $t_0 \dots t_k$, evaluate forecast on $t_{k+1} \dots t_{k+h}$, roll forward).
- Never shuffle time-series observations randomly across train/test splits.
