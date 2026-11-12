import React from 'react';
import { Activity, Compass, Cpu, Database, Network, RefreshCw, ShieldAlert } from 'lucide-react';
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
    { id: 'signals', label: 'RADAR & SIGNALS', icon: Activity },
    { id: 'trends', label: 'TRAJECTORIES', icon: Compass },
    { id: 'graph', label: 'GRAPH MATRIX', icon: Network },
    { id: 'investigate', label: 'DOSSIERS', icon: ShieldAlert },
  ];

  return (
    <header className="border-b border-vantage-700 bg-vantage-900/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectTab('signals')}>
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-vantage-accent to-vantage-neon flex items-center justify-center font-mono font-bold text-black text-lg shadow-lg shadow-vantage-accent/20">
            V
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold tracking-wider text-lg text-white">VANTAGE</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-vantage-accent/10 text-vantage-accent border border-vantage-accent/30">
                PROD v0.1
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono tracking-tight -mt-0.5">
              Multimodal Temporal Intelligence
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-md text-xs font-mono font-medium transition-all ${
                  active
                    ? 'bg-vantage-800 text-vantage-accent border border-vantage-accent/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-vantage-850'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${active ? 'text-vantage-accent' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Action & Telemetry */}
        <div className="flex items-center space-x-4">
          {stats && (
            <div className="hidden lg:flex items-center space-x-3 text-[11px] font-mono text-slate-400 border-r border-vantage-700 pr-4">
              <div className="flex items-center space-x-1.5">
                <Database className="w-3 h-3 text-slate-500" />
                <span>{stats.database.entities} ent</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <Activity className="w-3 h-3 text-vantage-surge" />
                <span className="text-vantage-surge font-semibold">{stats.database.signals} sig</span>
              </div>
            </div>
          )}

          <button
            onClick={onTriggerIngest}
            disabled={ingestRunning}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-mono font-medium transition-all ${
              ingestRunning
                ? 'bg-vantage-800 text-slate-500 border border-vantage-700 cursor-not-allowed'
                : 'bg-vantage-accent/10 text-vantage-accent hover:bg-vantage-accent/20 border border-vantage-accent/40 hover:shadow-lg hover:shadow-vantage-accent/10'
            }`}
            title="Scan GitHub, HuggingFace, PyPI, arXiv, and HackerNews"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${ingestRunning ? 'animate-spin text-vantage-accent' : ''}`} />
            <span>{ingestRunning ? 'SCANNING RADAR...' : 'SWEEP ADAPTERS'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
