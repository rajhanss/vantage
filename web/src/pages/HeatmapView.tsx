import React from 'react';
import { Shield, CheckCircle, AlertTriangle } from 'lucide-react';
import type { CategoryScore } from '../types';

interface HeatmapViewProps {
  categories: CategoryScore[];
  onSelectCategory?: (category: string) => void;
}

export const HeatmapView: React.FC<HeatmapViewProps> = ({ categories }) => {
  return (
    <div className="max-w-6xl mx-auto py-8 px-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-[var(--vt-text-main)] mb-1">
          OWASP Top 10 for Agentic Applications
        </h1>
        <p className="text-xs text-[var(--vt-text-secondary)]">
          Category-by-category attack success rate, binomial confidence intervals, and active vulnerability coverage.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((cat) => {
          const isClean = cat.successful_attacks === 0;
          const asrPct = (cat.attack_success_rate * 100).toFixed(1);

          return (
            <div
              key={cat.category}
              className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5 flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-[var(--vt-bg-hover)] text-[var(--vt-accent-primary)] border border-[var(--vt-border-subtle)]">
                      {cat.category}
                    </span>
                    <h2 className="text-sm font-semibold text-[var(--vt-text-main)]">
                      {cat.category_name}
                    </h2>
                  </div>
                  <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded border ${
                      isClean
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                    }`}
                  >
                    {isClean ? 'Resilient' : `${cat.findings_count} Vulnerable`}
                  </span>
                </div>

                <div className="flex items-baseline justify-between mt-3">
                  <span className="text-xs text-[var(--vt-text-secondary)]">
                    Attack Success Rate
                  </span>
                  <span className="font-mono text-base font-bold text-[var(--vt-text-main)]">
                    {asrPct}%
                  </span>
                </div>

                {/* ASR Progress Bar */}
                <div className="w-full bg-[var(--vt-bg-app)] h-2 rounded-full overflow-hidden mt-1.5 border border-[var(--vt-border-subtle)]">
                  <div
                    className={`h-full ${
                      cat.attack_success_rate > 0.4
                        ? 'bg-rose-500'
                        : cat.attack_success_rate > 0
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.max(cat.attack_success_rate * 100, 4)}%` }}
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-[var(--vt-border-subtle)] grid grid-cols-3 text-center font-mono text-[11px] text-[var(--vt-text-dim)]">
                <div>
                  <span className="block text-[var(--vt-text-secondary)] font-semibold">
                    {cat.total_scenarios}
                  </span>
                  Scenarios
                </div>
                <div>
                  <span className="block text-[var(--vt-text-secondary)] font-semibold">
                    {cat.total_trials}
                  </span>
                  Trials
                </div>
                <div>
                  <span className="block text-[var(--vt-text-secondary)] font-semibold">
                    [{(cat.wilson_lower * 100).toFixed(0)}%, {(cat.wilson_upper * 100).toFixed(0)}%]
                  </span>
                  95% Wilson
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
