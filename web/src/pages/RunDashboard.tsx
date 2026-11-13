import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle,
  FileText,
  Download,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Code2,
} from 'lucide-react';
import type { Finding, RunSummary } from '../types';
import { api } from '../api/client';

interface RunDashboardProps {
  summary: RunSummary | null;
  onLaunchNew: () => void;
}

export const RunDashboard: React.FC<RunDashboardProps> = ({ summary, onLaunchNew }) => {
  const [expandedFinding, setExpandedFinding] = useState<string | null>(null);

  if (!summary) {
    return (
      <div className="max-w-5xl mx-auto py-16 px-6 text-center">
        <div className="w-12 h-12 rounded-lg bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] flex items-center justify-center mx-auto mb-4 text-[var(--vt-accent-primary)]">
          <ShieldAlert size={24} aria-hidden="true" />
        </div>
        <h2 className="text-xl font-bold mb-2">No Security Assessment Run Loaded</h2>
        <p className="text-sm text-[var(--vt-text-secondary)] max-w-md mx-auto mb-6">
          Execute an adversarial evaluation against a target agent to generate reproducible findings and deterministic canary evidence.
        </p>
        <button
          type="button"
          onClick={onLaunchNew}
          className="px-4 py-2 rounded-md text-xs font-semibold bg-[var(--vt-accent-primary)] hover:bg-[var(--vt-accent-primary-hover)] text-white inline-flex items-center gap-2 transition-colors duration-150"
        >
          <span>Launch First Assessment</span>
        </button>
      </div>
    );
  }

  const gradeColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'B':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
      case 'C':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'D':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  const severityColor = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/40';
      case 'HIGH':
        return 'bg-orange-500/15 text-orange-400 border-orange-500/40';
      case 'MEDIUM':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/40';
      default:
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40';
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-6 space-y-8">
      {/* Executive Summary Card */}
      <section className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-[var(--vt-border-subtle)]">
          <div>
            <div className="flex items-center gap-3 mb-1.5">
              <h1 className="text-xl font-bold tracking-tight text-[var(--vt-text-main)]">
                {summary.target_name}
              </h1>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[var(--vt-bg-hover)] text-[var(--vt-text-secondary)] border border-[var(--vt-border-subtle)]">
                {summary.target_mode}
              </span>
            </div>
            <p className="text-xs text-[var(--vt-text-secondary)] font-mono">
              Run ID: {summary.run_id} | Completed in {summary.duration_ms.toFixed(1)} ms
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <span className="block text-xs text-[var(--vt-text-dim)] font-medium">
                Risk grade
              </span>
              <span
                className={`inline-block font-extrabold text-2xl px-3 py-0.5 rounded border mt-0.5 ${gradeColor(
                  summary.risk_grade
                )}`}
              >
                {summary.risk_grade}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <a
                href={api.getReportUrl(summary.run_id, 'html')}
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded text-xs font-medium bg-[var(--vt-bg-hover)] hover:bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] text-[var(--vt-text-main)] flex items-center gap-1.5 transition-colors duration-150"
              >
                <Download size={13} aria-hidden="true" />
                <span>HTML Report</span>
              </a>
              <a
                href={api.getReportUrl(summary.run_id, 'markdown')}
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded text-xs font-medium bg-[var(--vt-bg-hover)] hover:bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] text-[var(--vt-text-main)] flex items-center gap-1.5 transition-colors duration-150"
              >
                <FileText size={13} aria-hidden="true" />
                <span>Markdown</span>
              </a>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6">
          <div className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-4">
            <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
              Attack Success Rate (ASR)
            </span>
            <span className="text-2xl font-bold font-mono text-[var(--vt-text-main)]">
              {(summary.overall_asr * 100).toFixed(1)}%
            </span>
            <span className="text-[10px] text-[var(--vt-text-dim)] block mt-1">
              {summary.successful_attacks} / {summary.total_trials} trials breached
            </span>
          </div>

          <div className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-4">
            <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
              95% Wilson Interval
            </span>
            <span className="text-lg font-bold font-mono text-[var(--vt-text-main)]">
              [{(summary.wilson_lower * 100).toFixed(1)}%, {(summary.wilson_upper * 100).toFixed(1)}%]
            </span>
            <span className="text-[10px] text-[var(--vt-text-dim)] block mt-1">
              Binomial statistical confidence
            </span>
          </div>

          <div className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-4">
            <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
              Scenarios Evaluated
            </span>
            <span className="text-2xl font-bold font-mono text-[var(--vt-text-main)]">
              {summary.total_scenarios}
            </span>
            <span className="text-[10px] text-[var(--vt-text-dim)] block mt-1">
              Across OWASP Top 10 categories
            </span>
          </div>

          <div className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-4">
            <span className="text-[11px] text-[var(--vt-text-secondary)] block mb-1">
              Active Findings
            </span>
            <span className="text-2xl font-bold font-mono text-[var(--vt-text-main)]">
              {summary.findings.filter((f) => f.successful_attacks > 0).length}
            </span>
            <span className="text-[10px] text-[var(--vt-text-dim)] block mt-1">
              Canaries verified in trials
            </span>
          </div>
        </div>
      </section>

      {/* Vulnerability Findings Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[var(--vt-text-main)] flex items-center gap-2">
            <AlertTriangle size={16} className="text-[var(--vt-accent-primary)]" aria-hidden="true" />
            <span>Vulnerability Findings ({summary.findings.length})</span>
          </h2>
        </div>

        <div className="space-y-3">
          {summary.findings.map((f: Finding) => {
            const isExpanded = expandedFinding === f.id;
            const isVulnerable = f.successful_attacks > 0;

            return (
              <div
                key={f.id}
                className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5 transition-colors duration-150"
              >
                <div
                  className="flex items-start justify-between cursor-pointer select-none"
                  onClick={() => setExpandedFinding(isExpanded ? null : f.id)}
                >
                  <div className="space-y-1.5 flex-1 pr-4">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${severityColor(f.severity)}`}>
                        {f.severity}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--vt-bg-hover)] text-[var(--vt-text-secondary)] border border-[var(--vt-border-subtle)]">
                        {f.category}
                      </span>
                      <h3 className="text-sm font-semibold text-[var(--vt-text-main)]">
                        {f.scenario_name}
                      </h3>
                    </div>
                    <p className="text-xs text-[var(--vt-text-secondary)] font-mono">
                      ASR: {(f.attack_success_rate * 100).toFixed(1)}% ({f.successful_attacks}/{f.trials_run} trials) | 95% Wilson: [{(f.wilson_lower * 100).toFixed(1)}%, {(f.wilson_upper * 100).toFixed(1)}%]
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`text-xs font-semibold px-2.5 py-1 rounded border ${
                        isVulnerable
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      }`}
                    >
                      {isVulnerable ? 'Canary Breached' : 'Resisted'}
                    </span>
                    <button type="button" className="text-[var(--vt-text-dim)]" aria-label="Toggle details">
                      {isExpanded ? <ChevronDown size={18} aria-hidden="true" /> : <ChevronRight size={18} aria-hidden="true" />}
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-[var(--vt-border-subtle)] space-y-4">
                    <div>
                      <h4 className="text-xs font-semibold text-[var(--vt-text-secondary)] mb-1">
                        Deterministic Canary Evidence
                      </h4>
                      <div className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-3 font-mono text-xs text-[var(--vt-text-main)]">
                        {f.canary_summary}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-xs font-semibold text-[var(--vt-text-secondary)] mb-1">
                        Remediation Guidance
                      </h4>
                      <p className="text-xs text-[var(--vt-accent-primary)] leading-relaxed">
                        {f.remediation_hint}
                      </p>
                    </div>

                    {f.sample_transcript && f.sample_transcript.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-[var(--vt-text-secondary)] mb-1 flex items-center gap-1.5">
                          <Code2 size={13} aria-hidden="true" />
                          <span>Trial Transcript (Redacted)</span>
                        </h4>
                        <div className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-3 font-mono text-xs space-y-2 max-h-64 overflow-y-auto">
                          {f.sample_transcript.map((entry, idx) => (
                            <div key={idx} className="leading-snug">
                              <span className="text-[var(--vt-text-dim)] text-[11px] block">
                                [{entry.role}]
                              </span>
                              <span className="text-[var(--vt-text-main)] whitespace-pre-wrap">
                                {entry.content}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
};
