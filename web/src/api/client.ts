import type { RunComparison, RunConfig, RunSummary, Scenario } from '../types';

const BASE_URL = (import.meta as any).env?.VITE_API_URL || '';

export const api = {
  async getHealth(): Promise<{ status: string; service: string; version: string }> {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async listScenarios(category?: string): Promise<Scenario[]> {
    const url = category ? `${BASE_URL}/api/scenarios?category=${category}` : `${BASE_URL}/api/scenarios`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch scenarios');
    return res.json();
  },

  async getScenario(id: string): Promise<Scenario> {
    const res = await fetch(`${BASE_URL}/api/scenarios/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch scenario ${id}`);
    return res.json();
  },

  async listRuns(): Promise<RunSummary[]> {
    const res = await fetch(`${BASE_URL}/api/runs`);
    if (!res.ok) throw new Error('Failed to list runs');
    return res.json();
  },

  async getRun(runId: string): Promise<RunSummary> {
    const res = await fetch(`${BASE_URL}/api/runs/${runId}`);
    if (!res.ok) throw new Error(`Failed to fetch run ${runId}`);
    return res.json();
  },

  async createRun(config: RunConfig): Promise<RunSummary> {
    const res = await fetch(`${BASE_URL}/api/runs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!res.ok) throw new Error('Failed to execute evaluation run');
    return res.json();
  },

  async killRun(runId: string): Promise<{ status: string }> {
    const res = await fetch(`${BASE_URL}/api/runs/${runId}/kill`, { method: 'POST' });
    if (!res.ok) throw new Error(`Failed to kill run ${runId}`);
    return res.json();
  },

  async compareRuns(baselineId: string, hardenedId: string): Promise<RunComparison> {
    const res = await fetch(`${BASE_URL}/api/compare?baseline_id=${baselineId}&hardened_id=${hardenedId}`);
    if (!res.ok) throw new Error('Failed to compare runs');
    return res.json();
  },

  getReportUrl(runId: string, format: 'json' | 'markdown' | 'html'): string {
    return `${BASE_URL}/api/reports/${runId}?format=${format}`;
  },
};
