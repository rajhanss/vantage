import React, { useState } from 'react';
import { GitCompare, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import type { RunComparison, RunSummary } from '../types';
import { api } from '../api/client';

interface CompareViewProps {
  runs: RunSummary[];
}

export const CompareView: React.FC<CompareViewProps> = ({ runs }) => {
  const [baselineId, setBaselineId] = useState<string>(runs[1]?.run_id || runs[0]?.run_id || '');
  const [hardenedId, setHardenedId] = useState<string>(runs[0]?.run_id || '');
  const [comparison, setComparison] = useState<RunComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!baselineId || !hardenedId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.compareRuns(baselineId, hardenedId);
      setComparison(res);
    } catch (err: any) {
      setError(err.message || 'Failed to compare runs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-[var(--vt-text-main)] mb-1">
          Defense Efficacy Comparison
        </h1>
        <p className="text-xs text-[var(--vt-text-secondary)]">
          Compare a baseline vulnerable run against a hardened defense run to quantitatively measure security delta.
        </p>
      </div>

      {/* Selector Card */}
      <div className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5 flex flex-col md:flex-row items-center gap-4">
        <div className="flex-1 w-full">
          <label className="text-[11px] font-semibold text-[var(--vt-text-secondary)] block mb-1">
            Baseline Target Run (Vulnerable)
          </label>
          <select
            value={baselineId}
            onChange={(e) => setBaselineId(e.target.value)}
            className="w-full bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded px-3 py-2 text-xs font-mono text-[var(--vt-text-main)] focus:outline-none focus:border-[var(--vt-accent-primary)]"
          >
            {runs.map((r) => (
              <option key={r.run_id} value={r.run_id}>
                {r.target_name} ({r.target_mode}) — ASR: {(r.overall_asr * 100).toFixed(0)}% [Grade {r.risk_grade}]
              </option>
            ))}
          </select>
        </div>

        <div className="hidden md:flex items-center text-[var(--vt-text-dim)] pt-5">
          <ArrowRight size={20} aria-hidden="true" />
        </div>

        <div className="flex-1 w-full">
          <label className="text-[11px] font-semibold text-[var(--vt-text-secondary)] block mb-1">
            Hardened Defense Run
          </label>
          <select
            value={hardenedId}
            onChange={(e) => setHardenedId(e.target.value)}
            className="w-full bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded px-3 py-2 text-xs font-mono text-[var(--vt-text-main)] focus:outline-none focus:border-[var(--vt-accent-primary)]"
          >
            {runs.map((r) => (
              <option key={r.run_id} value={r.run_id}>
                {r.target_name} ({r.target_mode}) — ASR: {(r.overall_asr * 100).toFixed(0)}% [Grade {r.risk_grade}]
              </option>
            ))}
          </select>
        </div>

        <div className="w-full md:w-auto pt-0 md:pt-5">
          <button
            type="button"
            onClick={handleCompare}
            disabled={loading || !baselineId || !hardenedId}
            className="w-full md:w-auto px-4 py-2 rounded-md text-xs font-semibold bg-[var(--vt-accent-primary)] hover:bg-[var(--vt-accent-primary-hover)] text-white transition-colors duration-150 disabled:opacity-50"
          >
            {loading ? 'Comparing...' : 'Compare Runs'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded p-4 text-xs text-rose-400">
          {error}
        </div>
      )}

      {comparison && (
        <div className="space-y-6">
          {/* Comparison Scorecard */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5">
              <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
                Security Delta (Δ ASR)
              </span>
              <span className="text-2xl font-bold font-mono text-emerald-400">
                +{(comparison.asr_delta * 100).toFixed(1)}%
              </span>
              <span className="text-[10px] text-[var(--vt-text-dim)] block mt-1">
                Vulnerability reduction
              </span>
            </div>

            <div className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5">
              <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
                Risk Grade Progression
              </span>
              <div className="flex items-center gap-2 mt-1">
                <span className="font-extrabold text-xl px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
                  {comparison.baseline_grade}
                </span>
                <ArrowRight size={14} className="text-[var(--vt-text-dim)]" aria-hidden="true" />
                <span className="font-extrabold text-xl px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {comparison.hardened_grade}
                </span>
              </div>
            </div>

            <div className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5">
              <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
                Resolved Scenarios
              </span>
              <span className="text-2xl font-bold font-mono text-emerald-400">
                {comparison.resolved_scenarios.length}
              </span>
              <span className="text-[10px] text-[var(--vt-text-dim)] block mt-1">
                Attacks mitigated by defense
              </span>
            </div>

            <div className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5">
              <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
                Persistent Canaries
              </span>
              <span className="text-2xl font-bold font-mono text-amber-400">
                {comparison.persistent_scenarios.length}
              </span>
              <span className="text-[10px] text-[var(--vt-text-dim)] block mt-1">
                Remaining open vectors
              </span>
            </div>
          </div>

          {/* Category Delta Matrix */}
          <div className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-6">
            <h2 className="text-sm font-bold text-[var(--vt-text-main)] mb-4">
              Category Delta Matrix (OWASP ASI01 - ASI10)
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {Object.entries(comparison.category_deltas).map(([cat, delta]) => {
                const isPositive = delta > 0;
                return (
                  <div
                    key={cat}
                    className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-3 text-center font-mono"
                  >
                    <span className="text-[11px] text-[var(--vt-text-dim)] block">{cat}</span>
                    <span
                      className={`text-base font-bold block mt-1 ${
                        isPositive ? 'text-emerald-400' : 'text-[var(--vt-text-secondary)]'
                      }`}
                    >
                      {isPositive ? `+${(delta * 100).toFixed(0)}%` : '0%'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
