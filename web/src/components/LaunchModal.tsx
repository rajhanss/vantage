import React, { useState } from 'react';
import { X, Play, ShieldAlert, Cpu } from 'lucide-react';
import type { OwaspCategory, RunConfig, TargetSpec } from '../types';

interface LaunchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLaunch: (config: RunConfig) => Promise<void>;
  isLaunching: boolean;
}

export const LaunchModal: React.FC<LaunchModalProps> = ({
  isOpen,
  onClose,
  onLaunch,
  isLaunching,
}) => {
  const [targetType, setTargetType] = useState<'vulnerable' | 'hardened' | 'custom'>('vulnerable');
  const [trialsCount, setTrialsCount] = useState<number>(2);
  const [stepBudget, setStepBudget] = useState<number>(15);
  const [customEndpoint, setCustomEndpoint] = useState<string>('http://localhost:8000');
  const [selectedCats, setSelectedCats] = useState<OwaspCategory[]>([
    'ASI01',
    'ASI02',
    'ASI03',
    'ASI04',
    'ASI05',
    'ASI06',
    'ASI07',
    'ASI08',
    'ASI09',
    'ASI10',
  ]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const spec: TargetSpec = {
      name:
        targetType === 'vulnerable'
          ? 'Testbed-ToyAgent'
          : targetType === 'hardened'
          ? 'Hardened-ToyAgent'
          : 'External-Agent',
      type: targetType === 'custom' ? 'http' : 'in_process',
      endpoint: targetType === 'custom' ? customEndpoint : 'inprocess://testbed',
      mode: targetType === 'hardened' ? 'hardened' : 'vulnerable',
      timeout_sec: 30.0,
    };

    const config: RunConfig = {
      target_spec: spec,
      selected_categories: selectedCats,
      selected_scenarios: [],
      trials_per_scenario: trialsCount,
      seed: 42,
      max_budget_steps: stepBudget,
      max_budget_time_sec: 30.0,
    };

    await onLaunch(config);
  };

  const toggleCat = (cat: OwaspCategory) => {
    if (selectedCats.includes(cat)) {
      if (selectedCats.length > 1) {
        setSelectedCats(selectedCats.filter((c) => c !== cat));
      }
    } else {
      setSelectedCats([...selectedCats, cat]);
    }
  };

  const allCategories: OwaspCategory[] = [
    'ASI01',
    'ASI02',
    'ASI03',
    'ASI04',
    'ASI05',
    'ASI06',
    'ASI07',
    'ASI08',
    'ASI09',
    'ASI10',
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
      <div className="bg-[var(--vt-bg-card)] border border-[var(--vt-border-subtle)] rounded-lg w-full max-w-lg p-6 space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-[var(--vt-border-subtle)]">
          <div className="flex items-center gap-2.5">
            <ShieldAlert size={18} className="text-[var(--vt-accent-primary)]" aria-hidden="true" />
            <h2 className="text-base font-bold text-[var(--vt-text-main)]">
              Configure Security Assessment
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--vt-text-dim)] hover:text-[var(--vt-text-main)] transition-colors duration-150"
            aria-label="Close modal"
          >
            <X size={18} aria-hidden="true" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Target Preset Selection */}
          <div>
            <label className="text-xs font-semibold text-[var(--vt-text-secondary)] block mb-1.5">
              Select Target Mode
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setTargetType('vulnerable')}
                className={`p-3 rounded border text-left transition-colors duration-150 ${
                  targetType === 'vulnerable'
                    ? 'border-[var(--vt-accent-primary)] bg-[var(--vt-bg-hover)]'
                    : 'border-[var(--vt-border-subtle)] bg-[var(--vt-bg-app)]'
                }`}
              >
                <span className="block text-xs font-bold text-[var(--vt-text-main)]">
                  ToyAgent (Vulnerable)
                </span>
                <span className="block text-[11px] text-[var(--vt-text-dim)] mt-0.5">
                  Standard unhardened agent
                </span>
              </button>

              <button
                type="button"
                onClick={() => setTargetType('hardened')}
                className={`p-3 rounded border text-left transition-colors duration-150 ${
                  targetType === 'hardened'
                    ? 'border-emerald-500 bg-[var(--vt-bg-hover)]'
                    : 'border-[var(--vt-border-subtle)] bg-[var(--vt-bg-app)]'
                }`}
              >
                <span className="block text-xs font-bold text-[var(--vt-text-main)]">
                  ToyAgent (Hardened)
                </span>
                <span className="block text-[11px] text-[var(--vt-text-dim)] mt-0.5">
                  Untrusted isolation defense
                </span>
              </button>
            </div>
          </div>

          {/* Trials & Budget Controls */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-[var(--vt-text-secondary)] block mb-1">
                Trials per Scenario
              </label>
              <select
                value={trialsCount}
                onChange={(e) => setTrialsCount(Number(e.target.value))}
                className="w-full bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded px-3 py-1.5 text-xs font-mono text-[var(--vt-text-main)] focus:outline-none focus:border-[var(--vt-accent-primary)]"
              >
                <option value={1}>1 Trial (Fast Smoke)</option>
                <option value={2}>2 Trials (Standard)</option>
                <option value={3}>3 Trials (Recommended)</option>
                <option value={5}>5 Trials (High Precision)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-[var(--vt-text-secondary)] block mb-1">
                Step Budget Cap
              </label>
              <input
                type="number"
                min={5}
                max={50}
                value={stepBudget}
                onChange={(e) => setStepBudget(Number(e.target.value))}
                className="w-full bg-[var(--vt-bg-app)] border border-[var(--vt-border-subtle)] rounded px-3 py-1.5 text-xs font-mono text-[var(--vt-text-main)] focus:outline-none focus:border-[var(--vt-accent-primary)]"
              />
            </div>
          </div>

          {/* OWASP Categories Selection */}
          <div>
            <label className="text-xs font-semibold text-[var(--vt-text-secondary)] block mb-1.5">
              Active OWASP Categories ({selectedCats.length} / 10)
            </label>
            <div className="flex flex-wrap gap-1.5">
              {allCategories.map((cat) => {
                const active = selectedCats.includes(cat);
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => toggleCat(cat)}
                    className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-colors duration-150 ${
                      active
                        ? 'bg-[var(--vt-accent-primary)] text-white'
                        : 'bg-[var(--vt-bg-app)] text-[var(--vt-text-dim)] border border-[var(--vt-border-subtle)]'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-[var(--vt-border-subtle)] flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded text-xs text-[var(--vt-text-secondary)] hover:text-[var(--vt-text-main)] transition-colors duration-150"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLaunching}
              className="px-4 py-2 rounded-md text-xs font-semibold bg-[var(--vt-accent-primary)] hover:bg-[var(--vt-accent-primary-hover)] text-white flex items-center gap-2 transition-colors duration-150 disabled:opacity-50"
            >
              <Play size={13} aria-hidden="true" />
              <span>{isLaunching ? 'Executing Assessment...' : 'Start Run'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
