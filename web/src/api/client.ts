import type {
  GraphData,
  InvestigationDossier,
  PlatformStats,
  Recommendation,
  Signal,
  TrendDetail,
} from '../types';

const API_BASE = '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!resp.ok) {
    const errorText = await resp.text();
    throw new Error(`API ${resp.status} (${resp.statusText}): ${errorText}`);
  }
  return resp.json();
}

export const api = {
  getStats: () => fetchJson<PlatformStats>('/api/v1/stats'),

  getSignals: (minZ = 0.0, limit = 50) =>
    fetchJson<Signal[]>(`/api/v1/signals?min_z_score=${minZ}&limit=${limit}`),

  getTrends: (limit = 30, entityType = '') =>
    fetchJson<TrendDetail[]>(
      `/api/v1/trends?limit=${limit}${entityType ? `&entity_type=${entityType}` : ''}`
    ),

  getTrend: (entityId: string) =>
    fetchJson<TrendDetail>(`/api/v1/trends/${encodeURIComponent(entityId)}`),

  getGraph: (limit = 120) =>
    fetchJson<GraphData>(`/api/v1/graph?limit=${limit}`),

  getInvestigations: (limit = 20) =>
    fetchJson<InvestigationDossier[]>(`/api/v1/investigations?limit=${limit}`),

  getInvestigation: (id: string) =>
    fetchJson<InvestigationDossier>(`/api/v1/investigations/${encodeURIComponent(id)}`),

  startInvestigation: (entityId: string) =>
    fetchJson<InvestigationDossier>('/api/v1/investigate', {
      method: 'POST',
      body: JSON.stringify({ entity_id: entityId }),
    }),

  getRecommendations: (entityId: string, topK = 10) =>
    fetchJson<Recommendation[]>(
      `/api/v1/recommendations?entity_id=${encodeURIComponent(entityId)}&top_k=${topK}`
    ),

  triggerIngest: () =>
    fetchJson<{ status: string; message: string }>('/api/v1/ingest/trigger', {
      method: 'POST',
    }),

  getIngestStatus: () =>
    fetchJson<{ running: boolean }>('/api/v1/ingest/status'),
};
