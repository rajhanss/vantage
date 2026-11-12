import React, { useState } from 'react';
import { Compass, ExternalLink, Shield, Cpu, TrendingUp } from 'lucide-react';
import type { TrendDetail, Recommendation } from '../types';
import { TrendChart } from '../components/TrendChart';
import { LifecycleBadge } from '../components/LifecycleBadge';

interface TrendsPageProps {
  trends: TrendDetail[];
  selectedTrend: TrendDetail | null;
  onSelectTrend: (trend: TrendDetail) => void;
  recommendations: Recommendation[];
  onStartInvestigation: (entityId: string) => void;
  investigating: boolean;
}

export const TrendsPage: React.FC<TrendsPageProps> = ({
  trends,
  selectedTrend,
  onSelectTrend,
  recommendations,
  onStartInvestigation,
  investigating,
}) => {
  const [search, setSearch] = useState('');

  const filtered = trends.filter((t) =>
    t.entity.name.toLowerCase().includes(search.toLowerCase())
  );

  const activeTrend = selectedTrend || (trends.length > 0 ? trends[0] : null);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* Left 4 Cols: Entity List */}
      <div className="lg:col-span-4 space-y-4">
        <div className="flex items-center justify-between border-b border-vantage-700 pb-3">
          <div className="flex items-center space-x-2">
            <Compass className="w-4 h-4 text-vantage-accent" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-white">
              Trajectories ({filtered.length})
            </h2>
          </div>
        </div>

        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter entities..."
          className="w-full px-3 py-2 bg-vantage-900 border border-vantage-700 rounded text-xs text-white placeholder-slate-500 focus:outline-none focus:border-vantage-accent"
        />

        <div className="space-y-2 max-h-[700px] overflow-y-auto pr-1">
          {filtered.map((t) => {
            const isSelected = activeTrend?.entity.id === t.entity.id;
            return (
              <div
                key={t.entity.id}
                onClick={() => onSelectTrend(t)}
                className={`p-3 rounded border cursor-pointer transition-colors ${
                  isSelected
                    ? 'bg-vantage-800 border-vantage-accent shadow-sm'
                    : 'bg-vantage-900 border-vantage-700 hover:border-vantage-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 bg-vantage-950 px-1.5 py-0.5 rounded border border-vantage-700 capitalize">
                    {t.entity.entity_type}
                  </span>
                  <LifecycleBadge stage={t.lifecycle_stage} size="sm" />
                </div>

                <div className="font-mono font-medium text-xs text-white mt-1.5 truncate">
                  {t.entity.name}
                </div>

                <div className="flex items-center justify-between mt-2 pt-2 border-t border-vantage-700/60 text-xs font-mono">
                  <span className="text-slate-400">
                    vel:{' '}
                    <span className={t.current_velocity >= 0 ? 'text-vantage-surge' : 'text-rose-400'}>
                      {t.current_velocity > 0 ? `+${t.current_velocity.toFixed(1)}` : t.current_velocity.toFixed(1)}
                    </span>
                  </span>
                  <span className="text-vantage-accent font-semibold">
                    {Math.round(t.momentum_score * 100)}% momentum
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right 8 Cols: Detail & Forecasting Deck */}
      <div className="lg:col-span-8 space-y-6">
        {activeTrend ? (
          <>
            {/* Header Card */}
            <div className="bg-vantage-900 border border-vantage-700 rounded p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-400 bg-vantage-950 px-2 py-0.5 rounded border border-vantage-700 capitalize">
                      {activeTrend.entity.entity_type}
                    </span>
                    <LifecycleBadge stage={activeTrend.lifecycle_stage} size="md" />
                  </div>

                  <h1 className="text-xl font-mono font-bold text-white mt-2 flex items-center space-x-2">
                    <span>{activeTrend.entity.name}</span>
                    {activeTrend.entity.primary_url && (
                      <a
                        href={activeTrend.entity.primary_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-slate-400 hover:text-vantage-accent"
                        title="Open source URL"
                      >
                        <ExternalLink className="w-4 h-4" aria-hidden="true" />
                      </a>
                    )}
                  </h1>

                  <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
                    {activeTrend.entity.description || 'No entity description provided by source adapter.'}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => onStartInvestigation(activeTrend.entity.id)}
                  disabled={investigating}
                  className="flex items-center space-x-2 px-3.5 py-2 rounded bg-vantage-accent text-white font-medium text-xs hover:bg-blue-600 transition-colors shadow-sm whitespace-nowrap self-start"
                >
                  <Shield className="w-4 h-4" aria-hidden="true" />
                  <span>{investigating ? 'Investigating...' : 'Investigate dossier'}</span>
                </button>
              </div>

              {/* Trajectory Metrics Strip */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-vantage-800">
                <div className="bg-vantage-950 p-3 rounded border border-vantage-700">
                  <div className="text-xs text-slate-400">Growth velocity</div>
                  <div className="text-base font-mono font-bold text-vantage-surge mt-0.5">
                    {activeTrend.current_velocity > 0
                      ? `+${activeTrend.current_velocity.toFixed(2)}`
                      : activeTrend.current_velocity.toFixed(2)}
                    /day
                  </div>
                </div>
                <div className="bg-vantage-950 p-3 rounded border border-vantage-700">
                  <div className="text-xs text-slate-400">Acceleration</div>
                  <div className="text-base font-mono font-bold text-slate-200 mt-0.5">
                    {activeTrend.acceleration > 0
                      ? `+${activeTrend.acceleration.toFixed(2)}`
                      : activeTrend.acceleration.toFixed(2)}
                  </div>
                </div>
                <div className="bg-vantage-950 p-3 rounded border border-vantage-700">
                  <div className="text-xs text-slate-400">Momentum score</div>
                  <div className="text-base font-mono font-bold text-vantage-accent mt-0.5">
                    {Math.round(activeTrend.momentum_score * 100)}%
                  </div>
                </div>
                <div className="bg-vantage-950 p-3 rounded border border-vantage-700">
                  <div className="text-xs text-slate-400">Historical error (MAPE)</div>
                  <div className="text-base font-mono font-bold text-slate-300 mt-0.5">
                    {activeTrend.forecast ? `${(activeTrend.forecast.historical_mape * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Time-Series & 30-Day Damped Holt-Winters Projection */}
            <div className="bg-vantage-900 border border-vantage-700 rounded p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-vantage-accent" aria-hidden="true" />
                    <span>Temporal trajectory and 30-day projection</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Damped Holt-Winters model with 80% and 95% empirical prediction intervals.
                  </p>
                </div>
              </div>

              <TrendChart
                observations={activeTrend.observations}
                forecast={activeTrend.forecast}
                metricName="Activity"
              />
            </div>

            {/* Recommendations: Similar Entities via Two-Tower Vector Space */}
            <div className="bg-vantage-900 border border-vantage-700 rounded p-6">
              <h3 className="text-sm font-semibold text-white flex items-center space-x-2 mb-3">
                <Cpu className="w-4 h-4 text-blue-400" aria-hidden="true" />
                <span>Similar entities (Two-tower cosine + MMR diversity)</span>
              </h3>

              {recommendations.length === 0 ? (
                <div className="text-xs text-slate-500 py-4 text-center">
                  No similar entity embeddings detected yet
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {recommendations.slice(0, 6).map((rec) => (
                    <div
                      key={rec.entity_id}
                      className="p-3 bg-vantage-950 border border-vantage-700 rounded flex items-start justify-between"
                    >
                      <div>
                        <div className="font-mono font-medium text-xs text-slate-200">
                          {rec.name}
                        </div>
                        <div className="text-xs text-slate-400 mt-0.5">{rec.explanation}</div>
                      </div>
                      <span className="text-xs font-mono font-semibold text-vantage-accent ml-2">
                        {Math.round(rec.relevance_score * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="h-96 flex items-center justify-center text-xs text-slate-500">
            Select an entity from the list to inspect its trajectory
          </div>
        )}
      </div>
    </div>
  );
};
