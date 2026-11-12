import React from 'react';
import { Shield, CheckCircle2, AlertOctagon, ExternalLink } from 'lucide-react';
import type { InvestigationDossier } from '../types';

interface InvestigationViewProps {
  dossiers: InvestigationDossier[];
  selectedDossier: InvestigationDossier | null;
  onSelectDossier: (d: InvestigationDossier) => void;
  loading: boolean;
}

export const InvestigationView: React.FC<InvestigationViewProps> = ({
  dossiers,
  selectedDossier,
  onSelectDossier,
  loading,
}) => {
  const active = selectedDossier || (dossiers.length > 0 ? dossiers[0] : null);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* Left 4 Cols: Dossier Index */}
      <div className="lg:col-span-4 space-y-4">
        <div className="flex items-center space-x-2 border-b border-vantage-700 pb-3">
          <Shield className="w-4 h-4 text-vantage-accent" aria-hidden="true" />
          <h2 className="text-sm font-semibold text-white">
            Investigation archive ({dossiers.length})
          </h2>
        </div>

        {loading ? (
          <div className="text-xs text-slate-500 py-8 text-center">
            Loading dossiers...
          </div>
        ) : dossiers.length === 0 ? (
          <div className="text-xs text-slate-500 py-8 text-center border border-dashed border-vantage-700 rounded p-4">
            No investigations conducted yet. Select any entity in Radar or Trajectories to initiate an investigation.
          </div>
        ) : (
          <div className="space-y-2 max-h-[700px] overflow-y-auto pr-1">
            {dossiers.map((d) => {
              const isSelected = active?.id === d.id;
              return (
                <div
                  key={d.id}
                  onClick={() => onSelectDossier(d)}
                  className={`p-3 rounded border cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-vantage-800 border-vantage-accent shadow-sm'
                      : 'bg-vantage-900 border-vantage-700 hover:border-vantage-600'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                    <span>{d.created_at.split('T')[0]}</span>
                    <span className="text-vantage-accent font-semibold">
                      {Math.round(d.confidence_score * 100)}% confidence
                    </span>
                  </div>

                  <div className="font-mono font-semibold text-xs text-white mt-1 truncate">
                    {d.entity_name}
                  </div>

                  <div className="text-xs text-slate-400 truncate mt-0.5">
                    {d.title}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Right 8 Cols: Dossier Document */}
      <div className="lg:col-span-8 space-y-6">
        {active ? (
          <div className="bg-vantage-900 border border-vantage-700 rounded p-8 space-y-6">
            {/* Dossier Header */}
            <div className="border-b border-vantage-700 pb-6">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span className="text-vantage-accent font-semibold">
                  Investigation #{active.id.slice(0, 8)}
                </span>
                <span>Observed: {active.created_at.slice(0, 10)}</span>
              </div>

              <h1 className="text-2xl font-bold text-white mt-2">
                {active.title}
              </h1>

              <div className="mt-3 flex items-center space-x-3 text-xs font-mono">
                <span className="text-slate-400 font-sans">Target:</span>
                <span className="text-vantage-accent font-semibold">{active.entity_name}</span>
                <span className="text-slate-600 font-sans">|</span>
                <span className="text-slate-400 font-sans">Confidence:</span>
                <span className="text-vantage-surge font-semibold">
                  {Math.round(active.confidence_score * 100)}%
                </span>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-slate-400">
                Executive summary
              </h3>
              <p className="text-sm text-slate-200 leading-relaxed bg-vantage-950 p-4 rounded border border-vantage-700">
                {active.summary}
              </p>
            </div>

            {/* Key Findings */}
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-slate-400 flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-vantage-surge" aria-hidden="true" />
                <span>Key findings and evidence attribution</span>
              </h3>
              <div className="space-y-2">
                {active.key_findings.map((f, i) => (
                  <div
                    key={i}
                    className="flex items-start space-x-3 text-xs text-slate-300 p-2.5 rounded bg-vantage-950 border border-vantage-700"
                  >
                    <span className="text-vantage-accent font-mono font-semibold">0{i + 1}.</span>
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Contradictions / Data Gaps if present */}
            {active.contradictions && active.contradictions.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-amber-400 flex items-center space-x-1.5">
                  <AlertOctagon className="w-3.5 h-3.5" aria-hidden="true" />
                  <span>Contradictions and unresolved signals</span>
                </h3>
                <div className="space-y-2">
                  {active.contradictions.map((c, i) => (
                    <div
                      key={i}
                      className="text-xs text-amber-300/90 p-2.5 rounded bg-amber-950/20 border border-amber-800/40"
                    >
                      {c}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Evidence Sources */}
            <div className="space-y-3 pt-4 border-t border-vantage-700">
              <h3 className="text-xs font-semibold text-slate-400 flex items-center space-x-1.5">
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
                <span>Primary evidence citations</span>
              </h3>
              <div className="space-y-2">
                {active.evidence_sources.map((src, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between text-xs p-3 rounded bg-vantage-950 border border-vantage-700"
                  >
                    <div className="min-w-0 pr-4">
                      <div className="text-white font-medium truncate">{src.title}</div>
                      <div className="text-xs text-slate-400 truncate">{src.snippet}</div>
                    </div>
                    {src.url && (
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-vantage-accent hover:underline text-xs whitespace-nowrap flex items-center space-x-1"
                      >
                        <span>Source</span>
                        <ExternalLink className="w-3 h-3" aria-hidden="true" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="h-96 flex items-center justify-center text-xs text-slate-500">
            No dossier selected
          </div>
        )}
      </div>
    </div>
  );
};
