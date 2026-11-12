import React, { useState } from 'react';
import { Activity, Flame, Filter, Zap, TrendingUp, Layers } from 'lucide-react';
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
      {/* Overview Header */}
      <div className="rounded border border-vantage-700 bg-vantage-900 p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Ecosystem intelligence radar
            </h1>
            <p className="mt-1.5 text-sm text-slate-400 max-w-2xl leading-relaxed">
              Monitoring telemetry across GitHub, Hugging Face, arXiv, PyPI, and HackerNews to detect emerging technologies, inflection points, and adoption curves.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 w-full md:w-auto">
            <div className="bg-vantage-950 border border-vantage-700 rounded p-3 text-center min-w-[100px]">
              <div className="text-xs text-slate-400">Signals active</div>
              <div className="text-xl font-mono font-bold text-vantage-surge mt-0.5">{signals.length}</div>
            </div>
            <div className="bg-vantage-950 border border-vantage-700 rounded p-3 text-center min-w-[100px]">
              <div className="text-xs text-slate-400">Surges (&gt;2.5σ)</div>
              <div className="text-xl font-mono font-bold text-vantage-accent mt-0.5">
                {signals.filter((s) => s.z_score >= 2.5).length}
              </div>
            </div>
            <div className="bg-vantage-950 border border-vantage-700 rounded p-3 text-center min-w-[100px]">
              <div className="text-xs text-slate-400">Tracked entities</div>
              <div className="text-xl font-mono font-bold text-white mt-0.5">{topTrends.length}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Signals Feed + Momentum Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Signals Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-vantage-700 pb-3">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-vantage-accent" aria-hidden="true" />
              <h2 className="text-sm font-semibold text-white">
                Statistical signals ({filteredSignals.length})
              </h2>
            </div>

            {/* Filter controls */}
            <div className="flex items-center space-x-1 text-xs">
              <Filter className="w-3.5 h-3.5 text-slate-500 mr-1" aria-hidden="true" />
              {['all', 'repository', 'model', 'package', 'paper', 'topic'].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFilterType(type)}
                  className={`px-2 py-0.5 rounded capitalize transition-colors ${
                    filterType === type
                      ? 'bg-vantage-accent text-white font-medium'
                      : 'text-slate-400 hover:text-white bg-vantage-800'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="h-64 flex items-center justify-center text-xs text-slate-500">
              Loading signal feed...
            </div>
          ) : filteredSignals.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-xs text-slate-500 border border-dashed border-vantage-700 rounded p-8 text-center">
              <Zap className="w-8 h-8 text-slate-600 mb-2" aria-hidden="true" />
              <span className="font-medium text-slate-400">No active signals exceeding current threshold</span>
              <span className="text-xs text-slate-500 mt-1">
                Click &quot;Sweep adapters&quot; in the header to ingest live telemetry.
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
          <div className="flex items-center space-x-2 border-b border-vantage-700 pb-3">
            <Flame className="w-4 h-4 text-vantage-warning" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-white">
              Momentum leaderboard
            </h2>
          </div>

          <div className="space-y-2">
            {topTrends.slice(0, 10).map((t, idx) => (
              <div
                key={t.entity.id}
                onClick={() => onInspectEntity(t.entity.id)}
                className="group flex items-center justify-between p-3 rounded bg-vantage-900 border border-vantage-700 hover:border-vantage-600 cursor-pointer transition-colors"
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <span className="font-mono text-xs text-slate-500 w-5 text-right">
                    {idx + 1}
                  </span>
                  <div className="min-w-0">
                    <div className="font-mono text-xs font-medium text-slate-200 group-hover:text-vantage-accent truncate">
                      {t.entity.name}
                    </div>
                    <div className="text-xs text-slate-500 capitalize">
                      {t.entity.entity_type}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 text-right">
                  <LifecycleBadge stage={t.lifecycle_stage} size="sm" />
                  <div className="font-mono text-xs font-semibold text-vantage-accent w-12 text-right">
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
