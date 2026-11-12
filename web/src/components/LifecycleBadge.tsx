import React from 'react';
import type { LifecycleStage } from '../types';

interface LifecycleBadgeProps {
  stage: LifecycleStage;
  size?: 'sm' | 'md';
}

const config: Record<
  LifecycleStage,
  { label: string; bg: string; text: string; border: string; dot: string }
> = {
  acceleration: {
    label: 'ACCELERATION',
    bg: 'bg-emerald-950/60',
    text: 'text-emerald-400',
    border: 'border-emerald-500/40',
    dot: 'bg-emerald-400 animate-pulse',
  },
  inflection: {
    label: 'INFLECTION',
    bg: 'bg-cyan-950/60',
    text: 'text-cyan-400',
    border: 'border-cyan-500/40',
    dot: 'bg-cyan-400',
  },
  saturation: {
    label: 'SATURATION',
    bg: 'bg-amber-950/60',
    text: 'text-amber-400',
    border: 'border-amber-500/40',
    dot: 'bg-amber-400',
  },
  decay: {
    label: 'DECAY',
    bg: 'bg-rose-950/60',
    text: 'text-rose-400',
    border: 'border-rose-500/40',
    dot: 'bg-rose-400',
  },
  emergence: {
    label: 'EMERGENCE',
    bg: 'bg-indigo-950/60',
    text: 'text-indigo-400',
    border: 'border-indigo-500/40',
    dot: 'bg-indigo-400',
  },
};

export const LifecycleBadge: React.FC<LifecycleBadgeProps> = ({ stage, size = 'sm' }) => {
  const c = config[stage] || config.emergence;
  const padding = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center space-x-1.5 rounded-full font-mono font-medium border ${c.bg} ${c.text} ${c.border} ${padding}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      <span>{c.label}</span>
    </span>
  );
};
