import React, { useState } from 'react';
import { ShieldAlert, CheckCircle2, AlertOctagon, ExternalLink, FileText, ChevronRight } from 'lucide-react';
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
        <div className="flex items-center space-x-2 border-b border-vantage-800 pb-3">
          <ShieldAlert className="w-4 h-4 text-vantage-neon" />
          <h2 className="font-mono text-sm font-bold text-white tracking-wide">
            INVESTIGATION ARCHIVE ({dossiers.length})
          </h2>
        </div>

        {loading ? (
          <div className="text-xs font-mono text-slate-500 py-8 text-center">
            LOADING DOSSIERS...
          </div>
        ) : dossiers.length === 0 ? (
          <div className="text-xs font-mono text-slate-500 py-8 text-center border border-dashed border-vantage-800 rounded p-4">
            NO INVESTIGATIONS CONDUCTED YET. SELECT ANY ENTITY IN RADAR OR TRAJECTORIES TO INITIATE AN INVESTIGATION.
          </div>
        ) : (
          <div className="space-y-2 max-h-[700px] overflow-y-auto pr-1">
            {dossiers.map((d) => {
              const isSelected = active?.id === d.id;
              return (
                <div
                  key={d.id}
                  onClick={() => onSelectDossier(d)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-vantage-800 border-vantage-neon shadow-lg shadow-vantage-neon/5'
                      : 'bg-vantage-900 border-vantage-800/80 hover:border-vantage-700'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span>{d.created_at.split('T')[0]}</span>
                    <span className="text-vantage-accent font-semibold">
                      {Math.round(d.confidence_score * 100)}% conf
                    </span>
                  </div>

                  <div className="font-mono font-bold text-xs text-white mt-1 truncate">
                    {d.entity_name}
                  </div>

                  <div className="text-[11px] text-slate-400 truncate mt-0.5">
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
          <div className="bg-vantage-900 border border-vantage-700 rounded-xl p-8 space-y-6">
            {/* Dossier Header */}
            <div className="border-b border-vantage-800 pb-6">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span className="uppercase tracking-widest text-vantage-neon font-bold">
                  INTELLIGENCE DOSSIER #{active.id.slice(0, 8)}
                </span>
                <span>OBSERVED: {active.created_at}</span>
              </div>

              <h1 className="text-2xl font-mono font-bold text-white mt-2">
                {active.title}
              </h1>

              <div className="mt-3 flex items-center space-x-3 text-xs font-mono">
                <span className="text-slate-400">Target:</span>
                <span className="text-vantage-accent font-bold">{active.entity_name}</span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">Confidence:</span>
                <span className="text-vantage-surge font-semibold">
                  {Math.round(active.confidence_score * 100)}%
                </span>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="space-y-2">
              <h3 className="font-mono text-xs uppercase tracking-wider text-slate-400 font-bold">
                EXECUTIVE SUMMARY
              </h3>
              <p className="text-sm text-slate-200 leading-relaxed bg-vantage-950/60 p-4 rounded-lg border border-vantage-800 font-mono">
                {active.summary}
              </p>
            </div>

            {/* Key Findings */}
            <div className="space-y-3">
              <h3 className="font-mono text-xs uppercase tracking-wider text-slate-400 font-bold flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-vantage-surge" />
                <span>KEY FINDINGS & EVIDENCE ATTRIBUTION</span>
              </h3>
              <div className="space-y-2">
                {active.key_findings.map((f, i) => (
                  <div
                    key={i}
                    className="flex items-start space-x-3 text-xs font-mono text-slate-300 p-2.5 rounded bg-vantage-950/40 border border-vantage-850"
                  >
                    <span className="text-vantage-accent font-bold">0{i + 1}.</span>
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Contradictions / Data Gaps if present */}
            {active.contradictions && active.contradictions.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-mono text-xs uppercase tracking-wider text-amber-400 font-bold flex items-center space-x-1.5">
                  <AlertOctagon className="w-3.5 h-3.5" />
                  <span>CONTRADICTIONS & UNRESOLVED SIGNALS</span>
                </h3>
                <div className="space-y-2">
                  {active.contradictions.map((c, i) => (
                    <div
                      key={i}
                      className="text-xs font-mono text-amber-300/80 p-2.5 rounded bg-amber-950/20 border border-amber-900/40"
                    >
                      {c}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Evidence Sources */}
            <div className="space-y-3 pt-4 border-t border-vantage-800">
              <h3 className="font-mono text-xs uppercase tracking-wider text-slate-400 font-bold flex items-center space-x-1.5">
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                <span>PRIMARY EVIDENCE CITATIONS</span>
              </h3>
              <div className="space-y-2">
                {active.evidence_sources.map((src, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between text-xs font-mono p-3 rounded bg-vantage-950/60 border border-vantage-800"
                  >
                    <div className="min-w-0 pr-4">
                      <div className="text-white font-semibold truncate">{src.title}</div>
                      <div className="text-[10px] text-slate-500 truncate">{src.snippet}</div>
                    </div>
                    {src.url && (
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-vantage-accent hover:underline text-[11px] whitespace-nowrap flex items-center space-x-1"
                      >
                        <span>SOURCE</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="h-96 flex items-center justify-center text-xs font-mono text-slate-500">
            NO DOSSIER SELECTED
          </div>
        )}
      </div>
    </div>
  );
};
