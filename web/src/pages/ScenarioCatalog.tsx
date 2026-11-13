import React, { useState } from 'react';
import { Compass, Search, Tag, ShieldCheck, ArrowRight } from 'lucide-react';
import type { Scenario } from '../types';

interface ScenarioCatalogProps {
  scenarios: Scenario[];
}

export const ScenarioCatalog: React.FC<ScenarioCatalogProps> = ({ scenarios }) => {
  const [filterCat, setFilterCat] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filtered = scenarios.filter((s) => {
    const matchesCat = filterCat === 'ALL' || s.category === filterCat;
    const matchesSearch =
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const categories = ['ALL', 'ASI01', 'ASI02', 'ASI03', 'ASI04', 'ASI05', 'ASI06', 'ASI07', 'ASI08', 'ASI09', 'ASI10'];

  return (
    <div className="max-w-6xl mx-auto py-8 px-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-[var(--vt-text-main)] mb-1">
          Scenario Catalog
        </h1>
        <p className="text-xs text-[var(--vt-text-secondary)]">
          Pre-packaged adversarial testing vectors mapped to the OWASP Top 10 for Agentic Applications.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-2 sm:pb-0">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setFilterCat(cat)}
              className={`px-2.5 py-1 rounded text-xs font-mono font-medium transition-colors duration-150 ${
                filterCat === cat
                  ? 'bg-[var(--vt-accent-primary)] text-white'
                  : 'bg-[var(--vt-bg-card)] text-[var(--vt-text-secondary)] border border-[var(--vt-border-subtle)] hover:bg-[var(--vt-bg-hover)]'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <Search size={14} className="absolute left-3 top-2.5 text-[var(--vt-text-dim)]" aria-hidden="true" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search scenario ID or title..."
            className="w-full pl-9 pr-3 py-1.5 rounded-md bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] text-xs text-[var(--vt-text-main)] placeholder-[var(--vt-text-dim)] focus:outline-none focus:border-[var(--vt-accent-primary)] font-mono"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {filtered.map((s) => (
          <div
            key={s.id}
            className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg p-5 space-y-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-[var(--vt-bg-hover)] text-[var(--vt-accent-primary)] border border-[var(--vt-border-subtle)]">
                    {s.id}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--vt-bg-app)] text-[var(--vt-text-dim)] border border-[var(--vt-border-subtle)]">
                    {s.category}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
                    {s.severity}
                  </span>
                </div>
                <h2 className="text-sm font-semibold text-[var(--vt-text-main)]">
                  {s.name}
                </h2>
              </div>
            </div>

            <p className="text-xs text-[var(--vt-text-secondary)] leading-relaxed">
              {s.description}
            </p>

            {/* Attack Steps */}
            <div>
              <span className="text-xs font-medium text-[var(--vt-text-dim)] block mb-2">
                Attack steps ({s.attack_steps.length})
              </span>
              <div className="space-y-1.5">
                {s.attack_steps.map((step) => (
                  <div
                    key={step.step_id}
                    className="bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded p-2.5 font-mono text-xs flex items-start gap-2"
                  >
                    <span className="text-[var(--vt-accent-primary)] font-bold text-[11px]">
                      [{step.step_type}]
                    </span>
                    <span className="text-[var(--vt-text-main)] flex-1">{step.content}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Canary Expectations */}
            <div>
              <span className="text-xs font-medium text-[var(--vt-text-dim)] block mb-1">
                Deterministic canary condition
              </span>
              <div className="flex flex-wrap gap-2">
                {s.canaries.map((can, idx) => (
                  <div
                    key={idx}
                    className="bg-[var(--vt-bg-hover)] border border-[var(--vt-border-subtle)] px-2.5 py-1 rounded text-xs font-mono text-[var(--vt-text-main)] flex items-center gap-1.5"
                  >
                    <ShieldCheck size={13} className="text-emerald-400" aria-hidden="true" />
                    <span>{can.type}</span>
                    {can.expected_token && (
                      <span className="text-amber-400 font-bold">: {can.expected_token}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Remediation */}
            <div className="pt-2 border-t border-[var(--vt-border-subtle)]">
              <span className="text-[11px] text-[var(--vt-accent-primary)] font-medium">
                Remediation: {s.remediation_hint}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
