"""Vantage core domain models and validation schemas."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid

from pydantic import BaseModel, Field


def new_id() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class EntityType(str, Enum):
    REPOSITORY = "repository"
    MODEL = "model"
    PACKAGE = "package"
    PAPER = "paper"
    TOPIC = "topic"
    COMMUNITY = "community"
    AUTHOR = "author"


class MetricType(str, Enum):
    STARS = "stars"
    DOWNLOADS = "downloads"
    FORKS = "forks"
    CITATIONS = "citations"
    MENTIONS = "mentions"
    COMMENT_COUNT = "comment_count"
    ENGAGEMENT = "engagement"


class SignalType(str, Enum):
    GROWTH_SURGE = "growth_surge"
    VELOCITY_SPIKE = "velocity_spike"
    ANOMALY = "anomaly"
    CROSS_PLATFORM_EMERGENCE = "cross_platform_emergence"


class LifecycleStage(str, Enum):
    EMERGENCE = "emergence"
    ACCELERATION = "acceleration"
    INFLECTION = "inflection"
    SATURATION = "saturation"
    DECAY = "decay"


# --- Core Relational Models ---

class Entity(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    entity_type: EntityType
    primary_url: str = ""
    description: str = ""
    domain: str = "technology"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class Observation(BaseModel):
    id: str = Field(default_factory=new_id)
    entity_id: str
    source_id: str
    metric_name: str
    metric_value: float
    observed_at: datetime = Field(default_factory=now_utc)
    collected_at: datetime = Field(default_factory=now_utc)


class Signal(BaseModel):
    id: str = Field(default_factory=new_id)
    entity_id: str
    entity_name: str
    entity_type: EntityType
    signal_type: SignalType
    z_score: float
    velocity: float
    acceleration: float
    confidence: float
    detected_at: datetime = Field(default_factory=now_utc)
    summary: str = ""


class ForecastPoint(BaseModel):
    date: str
    value: float
    lower_80: float
    upper_80: float
    lower_95: float
    upper_95: float


class TrendForecast(BaseModel):
    entity_id: str
    horizon_days: int = 30
    historical_mape: float = 0.05
    points: list[ForecastPoint] = Field(default_factory=list)


class TrendDetail(BaseModel):
    entity: Entity
    current_velocity: float
    acceleration: float
    momentum_score: float
    lifecycle_stage: LifecycleStage
    observations: list[Observation] = Field(default_factory=list)
    forecast: TrendForecast | None = None
    related_entities: list[str] = Field(default_factory=list)


class EvidenceSource(BaseModel):
    url: str
    title: str
    source_name: str
    published_at: str = ""
    snippet: str = ""
    reliability_score: float = 0.9


class InvestigationDossier(BaseModel):
    id: str = Field(default_factory=new_id)
    entity_id: str
    entity_name: str
    title: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    evidence_sources: list[EvidenceSource] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    confidence_score: float = 0.85
    created_at: datetime = Field(default_factory=now_utc)


class GraphNode(BaseModel):
    id: str
    name: str
    entity_type: EntityType
    degree: int = 1
    betweenness: float = 0.0
    community_id: int = 0


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float = 1.0
    relation_type: str = "co_occurs_with"


class GraphData(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    communities: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    entity_id: str
    name: str
    entity_type: EntityType
    relevance_score: float
    explanation: str
    tags: list[str] = Field(default_factory=list)
