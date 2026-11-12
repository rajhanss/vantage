import React from 'react';
import { ArrowUpRight, ArrowDownRight, Zap, AlertTriangle, ExternalLink } from 'lucide-react';
import type { Signal } from '../types';

interface SignalCardProps {
  signal: Signal;
  onInspect: (entityId: string) => void;
}

export const SignalCard: React.FC<SignalCardProps> = ({ signal, onInspect }) => {
  const isSurge = signal.signal_type === 'growth_surge' || signal.z_score >= 2.5;
  const isPositiveVelocity = signal.velocity >= 0;

  return (
    <div className="group relative bg-vantage-900 border border-vantage-700 hover:border-vantage-600 rounded p-4 transition-colors">
      {/* Top row: entity type & signal badge */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-400 bg-vantage-800 px-2 py-0.5 rounded border border-vantage-700">
          {signal.entity_type}
        </span>
        <div className="flex items-center space-x-1.5">
          <span
            className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded font-mono text-xs font-semibold border ${
              isSurge
                ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60'
                : 'bg-amber-950/40 text-amber-400 border-amber-800/60'
            }`}
          >
            {isSurge ? (
              <Zap className="w-3 h-3 text-emerald-400" aria-hidden="true" />
            ) : (
              <AlertTriangle className="w-3 h-3 text-amber-400" aria-hidden="true" />
            )}
            <span>Z={signal.z_score > 0 ? `+${signal.z_score.toFixed(1)}` : signal.z_score.toFixed(1)}σ</span>
          </span>
        </div>
      </div>

      {/* Entity name */}
      <h3
        onClick={() => onInspect(signal.entity_id)}
        className="font-mono font-semibold text-sm text-white group-hover:text-vantage-accent transition-colors truncate cursor-pointer"
        title={signal.entity_name}
      >
        {signal.entity_name}
      </h3>

      {/* Summary */}
      <p className="text-xs text-slate-400 line-clamp-2 mt-1 min-h-[2rem]">
        {signal.summary || `Detected ${signal.signal_type.replace('_', ' ')} with ${Math.round(signal.confidence * 100)}% confidence`}
      </p>

      {/* Metrics Footer */}
      <div className="mt-3 pt-3 border-t border-vantage-800 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1">
            {isPositiveVelocity ? (
              <ArrowUpRight className="w-3.5 h-3.5 text-vantage-surge" aria-hidden="true" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 text-rose-400" aria-hidden="true" />
            )}
            <span className={isPositiveVelocity ? 'text-vantage-surge font-semibold' : 'text-rose-400 font-semibold'}>
              {signal.velocity > 0 ? `+${signal.velocity.toFixed(1)}` : signal.velocity.toFixed(1)}/day
            </span>
          </div>

          <div className="text-slate-500 text-xs">
            accel: {signal.acceleration > 0 ? `+${signal.acceleration.toFixed(2)}` : signal.acceleration.toFixed(2)}
          </div>
        </div>

        <button
          type="button"
          onClick={() => onInspect(signal.entity_id)}
          className="text-slate-300 hover:text-vantage-accent transition-colors flex items-center space-x-1 text-xs font-sans"
        >
          <span>Inspect</span>
          <ExternalLink className="w-3 h-3" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
};
