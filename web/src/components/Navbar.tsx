import React from 'react';
import { Shield, Play, Layers, Compass, GitCompare } from 'lucide-react';

interface NavbarProps {
  activeTab: 'dashboard' | 'heatmap' | 'scenarios' | 'compare';
  onTabChange: (tab: 'dashboard' | 'heatmap' | 'scenarios' | 'compare') => void;
  onLaunchClick: () => void;
  isEvaluating?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  onTabChange,
  onLaunchClick,
  isEvaluating = false,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Evaluation Runs', icon: Layers },
    { id: 'heatmap', label: 'OWASP Matrix', icon: Shield },
    { id: 'scenarios', label: 'Scenario Catalog', icon: Compass },
    { id: 'compare', label: 'Defense Compare', icon: GitCompare },
  ] as const;

  return (
    <nav className="h-14 border-b border-[var(--vt-border-subtle)] bg-[var(--vt-bg-card)] px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded bg-[var(--vt-accent-primary)] flex items-center justify-center text-white font-bold text-xs tracking-tight">
            V
          </div>
          <div className="flex items-baseline gap-2">
            <span className="font-bold text-base tracking-tight text-[var(--vt-text-main)]">
              VANTAGE
            </span>
            <span className="text-[11px] font-mono text-[var(--vt-text-dim)]">
              v0.1.0
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onTabChange(item.id)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center gap-2 transition-colors duration-150 ${
                  active
                    ? 'bg-[var(--vt-bg-hover)] text-[var(--vt-text-main)] border border-[var(--vt-border-subtle)]'
                    : 'text-[var(--vt-text-secondary)] hover:text-[var(--vt-text-main)] hover:bg-[var(--vt-bg-hover)]'
                }`}
              >
                <Icon size={14} aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onLaunchClick}
          disabled={isEvaluating}
          className="px-3.5 py-1.5 rounded-md text-xs font-semibold bg-[var(--vt-accent-primary)] hover:bg-[var(--vt-accent-primary-hover)] text-white flex items-center gap-2 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play size={13} aria-hidden="true" />
          <span>{isEvaluating ? 'Evaluating Target...' : 'New Assessment'}</span>
        </button>
      </div>
    </nav>
  );
};
