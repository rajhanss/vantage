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
    <div className="group relative bg-vantage-900 border border-vantage-700/80 hover:border-vantage-accent/60 rounded-lg p-4 transition-all duration-200 hover:shadow-lg hover:shadow-vantage-accent/5">
      {/* Top row: entity type & signal badge */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 bg-vantage-800 px-2 py-0.5 rounded border border-vantage-700">
          {signal.entity_type}
        </span>
        <div className="flex items-center space-x-1.5">
          <span
            className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded font-mono text-[10px] font-semibold border ${
              isSurge
                ? 'bg-emerald-950/70 text-emerald-400 border-emerald-500/40'
                : 'bg-amber-950/70 text-amber-400 border-amber-500/40'
            }`}
          >
            {isSurge ? <Zap className="w-2.5 h-2.5" /> : <AlertTriangle className="w-2.5 h-2.5" />}
            <span>Z={signal.z_score > 0 ? `+${signal.z_score.toFixed(1)}` : signal.z_score.toFixed(1)}σ</span>
          </span>
        </div>
      </div>

      {/* Entity name */}
      <h3
        onClick={() => onInspect(signal.entity_id)}
        className="font-mono font-bold text-sm text-white group-hover:text-vantage-accent transition-colors truncate cursor-pointer"
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
              <ArrowUpRight className="w-3.5 h-3.5 text-vantage-surge" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 text-rose-400" />
            )}
            <span className={isPositiveVelocity ? 'text-vantage-surge' : 'text-rose-400'}>
              {signal.velocity > 0 ? `+${signal.velocity.toFixed(1)}` : signal.velocity.toFixed(1)}/d
            </span>
          </div>

          <div className="text-slate-500 text-[11px]">
            a={signal.acceleration > 0 ? `+${signal.acceleration.toFixed(2)}` : signal.acceleration.toFixed(2)}
          </div>
        </div>

        <button
          onClick={() => onInspect(signal.entity_id)}
          className="text-slate-400 hover:text-vantage-accent transition-colors flex items-center space-x-1 text-[11px]"
        >
          <span>ANALYZE</span>
          <ExternalLink className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
};
