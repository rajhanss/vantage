import React from 'react';
import type { LifecycleStage } from '../types';

interface LifecycleBadgeProps {
  stage: LifecycleStage;
  size?: 'sm' | 'md';
}

const config: Record<
  LifecycleStage,
  { label: string; bg: string; text: string; border: string }
> = {
  acceleration: {
    label: 'Acceleration',
    bg: 'bg-emerald-950/40',
    text: 'text-emerald-400',
    border: 'border-emerald-800/60',
  },
  inflection: {
    label: 'Inflection',
    bg: 'bg-blue-950/40',
    text: 'text-blue-400',
    border: 'border-blue-800/60',
  },
  saturation: {
    label: 'Saturation',
    bg: 'bg-amber-950/40',
    text: 'text-amber-400',
    border: 'border-amber-800/60',
  },
  decay: {
    label: 'Decay',
    bg: 'bg-rose-950/40',
    text: 'text-rose-400',
    border: 'border-rose-800/60',
  },
  emergence: {
    label: 'Emergence',
    bg: 'bg-slate-900',
    text: 'text-slate-300',
    border: 'border-slate-700',
  },
};

export const LifecycleBadge: React.FC<LifecycleBadgeProps> = ({ stage, size = 'sm' }) => {
  const c = config[stage] || config.emergence;
  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center rounded font-medium border ${c.bg} ${c.text} ${c.border} ${padding}`}
    >
      <span>{c.label}</span>
    </span>
  );
};
