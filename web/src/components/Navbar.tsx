import React from 'react';
import { Activity, Compass, Database, Network, RefreshCw, Shield } from 'lucide-react';
import type { PlatformStats } from '../types';

interface NavbarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  stats: PlatformStats | null;
  onTriggerIngest: () => void;
  ingestRunning: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  stats,
  onTriggerIngest,
  ingestRunning,
}) => {
  const navItems = [
    { id: 'signals', label: 'Signals & radar', icon: Activity },
    { id: 'trends', label: 'Trajectories', icon: Compass },
    { id: 'graph', label: 'Network matrix', icon: Network },
    { id: 'investigate', label: 'Dossiers', icon: Shield },
  ];

  return (
    <header className="border-b border-vantage-700 bg-vantage-900/95 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <button
          type="button"
          className="flex items-center space-x-3 text-left focus-visible:ring-2 focus-visible:ring-vantage-accent rounded p-1"
          onClick={() => onSelectTab('signals')}
        >
          <div className="w-8 h-8 rounded bg-vantage-accent text-white flex items-center justify-center font-mono font-bold text-base shadow-sm">
            V
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-base text-white tracking-normal">Vantage</span>
              <span className="px-1.5 py-0.5 rounded text-[11px] font-mono font-medium bg-vantage-800 text-vantage-accent border border-vantage-700">
                v0.1
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              Temporal intelligence platform
            </div>
          </div>
        </button>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-2" aria-label="Main navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectTab(item.id)}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  active
                    ? 'bg-vantage-800 text-white border border-vantage-600 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-vantage-850'
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? 'text-vantage-accent' : 'text-slate-400'}`} aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Telemetry & Action */}
        <div className="flex items-center space-x-4">
          {stats && (
            <div className="hidden lg:flex items-center space-x-3 text-xs text-slate-400 border-r border-vantage-700 pr-4">
              <div className="flex items-center space-x-1.5">
                <Database className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
                <span className="font-mono">{stats.database.entities} entities</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <Activity className="w-3.5 h-3.5 text-vantage-surge" aria-hidden="true" />
                <span className="text-vantage-surge font-mono font-semibold">{stats.database.signals} signals</span>
              </div>
            </div>
          )}

          <button
            type="button"
            onClick={onTriggerIngest}
            disabled={ingestRunning}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              ingestRunning
                ? 'bg-vantage-800 text-slate-500 border border-vantage-700 cursor-not-allowed'
                : 'bg-vantage-accent text-white hover:bg-blue-600 shadow-sm'
            }`}
            title="Scan GitHub, HuggingFace, PyPI, arXiv, and HackerNews"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${ingestRunning ? 'animate-spin' : ''}`}
              aria-hidden="true"
            />
            <span>{ingestRunning ? 'Scanning radar...' : 'Sweep adapters'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
