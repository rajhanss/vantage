"""
Two-tower feature-based recommender with MMR diversity re-ranking.
No neural network required — fast cosine similarity on hand-crafted feature vectors.
"""
from __future__ import annotations

import math
from typing import Sequence

from vantage.models.domain import Entity, EntityType, Observation, Recommendation

_ENTITY_TYPES = list(EntityType)
_N_TYPES = len(_ENTITY_TYPES)
_N_METRIC_SLOTS = 10
_VECTOR_DIM = _N_TYPES + _N_METRIC_SLOTS + 2  # types + metrics + [desc_len, domain_hash]


def _entity_vector(
    entity: Entity,
    observations: list[Observation],
) -> list[float]:
    """Fixed-dimension feature vector for cosine similarity computation."""
    # Type one-hot
    type_vec = [0.0] * _N_TYPES
    try:
        idx = _ENTITY_TYPES.index(entity.entity_type)
        type_vec[idx] = 1.0
    except ValueError:
        pass

    # Metric values (last 10 observations, normalised to [0, 1])
    metric_vals = [o.metric_value for o in observations[-_N_METRIC_SLOTS:]]
    while len(metric_vals) < _N_METRIC_SLOTS:
        metric_vals.append(0.0)
    max_val = max(metric_vals) + 1e-9
    metric_norm = [v / max_val for v in metric_vals]

    # Auxiliary features
    desc_len = min(1.0, len(entity.description) / 500.0)
    domain_hash = float(hash(entity.domain) % 1000) / 1000.0

    return type_vec + metric_norm + [desc_len, domain_hash]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0
    return dot / (norm_a * norm_b)


def _mmr_rerank(
    candidates: list[tuple[str, list[float], float]],
    top_k: int,
    lambda_: float = 0.7,
) -> list[tuple[str, float]]:
    """
    Maximal Marginal Relevance re-ranking.
    Balances relevance (cosine to query) with diversity (distance from selected set).
    """
    selected: list[tuple[str, list[float]]] = []
    remaining = list(candidates)
    result: list[tuple[str, float]] = []

    while remaining and len(result) < top_k:
        scores: list[tuple[int, float]] = []
        for idx, (eid, vec, rel) in enumerate(remaining):
            if not selected:
                redundancy = 0.0
            else:
                redundancy = max(
                    _cosine_similarity(vec, sel_vec) for _, sel_vec in selected
                )
            mmr_score = lambda_ * rel - (1.0 - lambda_) * redundancy
            scores.append((idx, mmr_score))

        best_idx, best_score = max(scores, key=lambda x: x[1])
        best = remaining.pop(best_idx)
        selected.append((best[0], best[1]))
        result.append((best[0], max(0.0, best_score)))

    return result


def recommend_similar(
    target_entity_id: str,
    all_entities: list[Entity],
    observations_map: dict[str, list[Observation]],
    top_k: int = 10,
) -> list[Recommendation]:
    """Return top-k entities most similar to the target, with MMR diversity."""
    target = next((e for e in all_entities if e.id == target_entity_id), None)
    if target is None:
        return []

    target_vec = _entity_vector(target, observations_map.get(target_entity_id, []))

    candidates: list[tuple[str, list[float], float]] = []
    for entity in all_entities:
        if entity.id == target_entity_id:
            continue
        vec = _entity_vector(entity, observations_map.get(entity.id, []))
        sim = _cosine_similarity(target_vec, vec)
        if sim > 0.01:  # Skip entirely dissimilar entities
            candidates.append((entity.id, vec, sim))

    candidates.sort(key=lambda x: x[2], reverse=True)
    top_candidates = candidates[: top_k * 4]
    selected = _mmr_rerank(top_candidates, top_k)

    entity_map = {e.id: e for e in all_entities}
    recommendations: list[Recommendation] = []
    for eid, score in selected:
        entity = entity_map.get(eid)
        if entity:
            recommendations.append(
                Recommendation(
                    entity_id=entity.id,
                    name=entity.name,
                    entity_type=entity.entity_type,
                    relevance_score=round(score, 4),
                    explanation=(
                        f"Similar to {target.name} — "
                        f"matched on {entity.entity_type.value} activity patterns"
                    ),
                    tags=[entity.entity_type.value, entity.domain],
                )
            )

    return recommendations
