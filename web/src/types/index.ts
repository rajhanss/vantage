export type EntityType =
  | 'repository'
  | 'model'
  | 'package'
  | 'paper'
  | 'topic'
  | 'community'
  | 'author';

export type SignalType =
  | 'growth_surge'
  | 'velocity_spike'
  | 'anomaly'
  | 'cross_platform_emergence';

export type LifecycleStage =
  | 'emergence'
  | 'acceleration'
  | 'inflection'
  | 'saturation'
  | 'decay';

export interface Entity {
  id: string;
  name: string;
  entity_type: EntityType;
  primary_url: string;
  description: string;
  domain: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Observation {
  id: string;
  entity_id: string;
  source_id: string;
  metric_name: string;
  metric_value: number;
  observed_at: string;
  collected_at: string;
}

export interface Signal {
  id: string;
  entity_id: string;
  entity_name: string;
  entity_type: EntityType;
  signal_type: SignalType;
  z_score: number;
  velocity: number;
  acceleration: number;
  confidence: number;
  detected_at: string;
  summary: string;
}

export interface ForecastPoint {
  date: string;
  value: number;
  lower_80: number;
  upper_80: number;
  lower_95: number;
  upper_95: number;
}

export interface TrendForecast {
  entity_id: string;
  horizon_days: number;
  historical_mape: number;
  points: ForecastPoint[];
}

export interface TrendDetail {
  entity: Entity;
  current_velocity: number;
  acceleration: number;
  momentum_score: number;
  lifecycle_stage: LifecycleStage;
  observations: Observation[];
  forecast?: TrendForecast | null;
  related_entities: string[];
}

export interface EvidenceSource {
  url: string;
  title: string;
  source_name: string;
  published_at?: string;
  snippet: string;
  reliability_score: number;
}

export interface InvestigationDossier {
  id: string;
  entity_id: string;
  entity_name: string;
  title: string;
  summary: string;
  key_findings: string[];
  evidence_sources: EvidenceSource[];
  contradictions: string[];
  confidence_score: number;
  created_at: string;
}

export interface GraphNode {
  id: string;
  name: string;
  entity_type: EntityType;
  degree: number;
  betweenness: number;
  community_id: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  relation_type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  communities: string[];
}

export interface Recommendation {
  entity_id: string;
  name: string;
  entity_type: EntityType;
  relevance_score: number;
  explanation: string;
  tags: string[];
}

export interface PlatformStats {
  version: string;
  environment: string;
  database: {
    entities: number;
    observations: number;
    signals: number;
    investigations: number;
  };
  adapters: string[];
}
