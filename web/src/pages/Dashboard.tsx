import React, { useState } from 'react';
import { Activity, Flame, ShieldAlert, Sparkles, Filter, Zap } from 'lucide-react';
import type { Signal, TrendDetail } from '../types';
import { SignalCard } from '../components/SignalCard';
import { LifecycleBadge } from '../components/LifecycleBadge';

interface DashboardProps {
  signals: Signal[];
  topTrends: TrendDetail[];
  onInspectEntity: (entityId: string) => void;
  loading: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({
  signals,
  topTrends,
  onInspectEntity,
  loading,
}) => {
  const [filterType, setFilterType] = useState<string>('all');

  const filteredSignals = signals.filter((s) => {
    if (filterType === 'all') return true;
    return s.entity_type === filterType;
  });

  return (
    <div className="space-y-8">
      {/* Hero Telemetry Banner */}
      <div className="relative overflow-hidden rounded-xl border border-vantage-700 bg-gradient-to-r from-vantage-900 via-vantage-850 to-vantage-900 p-6 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-vantage-accent/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center space-x-2 text-xs font-mono text-vantage-accent uppercase tracking-widest">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Real-Time Anomaly & Velocity Radar</span>
            </div>
            <h1 className="mt-1 text-2xl font-mono font-bold text-white tracking-tight">
              INTERNET INTELLIGENCE RADAR
            </h1>
            <p className="mt-1 text-xs text-slate-400 max-w-xl">
              Continuously monitoring cross-platform activity across GitHub repositories, HuggingFace models,
              arXiv papers, PyPI packages, and HackerNews discussions. Identifying statistical inflection points.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 w-full md:w-auto">
            <div className="bg-vantage-950/70 border border-vantage-700/80 rounded-lg p-3 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Signals Active</div>
              <div className="text-xl font-mono font-bold text-vantage-surge mt-0.5">{signals.length}</div>
            </div>
            <div className="bg-vantage-950/70 border border-vantage-700/80 rounded-lg p-3 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Surges (&gt;2.5σ)</div>
              <div className="text-xl font-mono font-bold text-vantage-accent mt-0.5">
                {signals.filter((s) => s.z_score >= 2.5).length}
              </div>
            </div>
            <div className="bg-vantage-950/70 border border-vantage-700/80 rounded-lg p-3 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Tracked Entities</div>
              <div className="text-xl font-mono font-bold text-white mt-0.5">{topTrends.length}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Signals Ticker + Momentum Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Signals Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-vantage-800 pb-3">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-vantage-accent" />
              <h2 className="font-mono text-sm font-bold text-white tracking-wide">
                STATISTICAL SIGNALS FEED ({filteredSignals.length})
              </h2>
            </div>

            {/* Filter pills */}
            <div className="flex items-center space-x-1 text-[11px] font-mono">
              <Filter className="w-3 h-3 text-slate-500 mr-1" />
              {['all', 'repository', 'model', 'package', 'paper', 'topic'].map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-2 py-0.5 rounded uppercase ${
                    filterType === type
                      ? 'bg-vantage-accent text-black font-semibold'
                      : 'text-slate-400 hover:text-white bg-vantage-800'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="h-64 flex items-center justify-center text-xs font-mono text-slate-500">
              POLLING RADAR DETECTORS...
            </div>
          ) : filteredSignals.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-xs font-mono text-slate-500 border border-dashed border-vantage-800 rounded-lg p-8 text-center">
              <Zap className="w-8 h-8 text-slate-600 mb-2" />
              <span>NO ACTIVE SIGNALS EXCEEDING CURRENT Z-SCORE THRESHOLD</span>
              <span className="text-[10px] text-slate-600 mt-1">
                Click &apos;SWEEP ADAPTERS&apos; above to ingest live telemetry from public ecosystems.
              </span>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {filteredSignals.map((signal) => (
                <SignalCard key={signal.id} signal={signal} onInspect={onInspectEntity} />
              ))}
            </div>
          )}
        </div>

        {/* Right Col: Momentum Leaderboard */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 border-b border-vantage-800 pb-3">
            <Flame className="w-4 h-4 text-vantage-warning" />
            <h2 className="font-mono text-sm font-bold text-white tracking-wide">
              MOMENTUM LEADERBOARD
            </h2>
          </div>

          <div className="space-y-2">
            {topTrends.slice(0, 10).map((t, idx) => (
              <div
                key={t.entity.id}
                onClick={() => onInspectEntity(t.entity.id)}
                className="group flex items-center justify-between p-3 rounded-lg bg-vantage-900 border border-vantage-800/80 hover:border-vantage-accent/50 cursor-pointer transition-all"
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <span className="font-mono text-xs font-bold text-slate-500 w-4 text-right">
                    #{idx + 1}
                  </span>
                  <div className="min-w-0">
                    <div className="font-mono text-xs font-semibold text-slate-200 group-hover:text-vantage-accent truncate">
                      {t.entity.name}
                    </div>
                    <div className="text-[10px] text-slate-500 uppercase font-mono">
                      {t.entity.entity_type}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 text-right">
                  <LifecycleBadge stage={t.lifecycle_stage} size="sm" />
                  <div className="font-mono text-xs font-bold text-vantage-accent w-12 text-right">
                    {Math.round(t.momentum_score * 100)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
