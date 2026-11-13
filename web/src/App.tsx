import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { RunDashboard } from './pages/RunDashboard';
import { HeatmapView } from './pages/HeatmapView';
import { ScenarioCatalog } from './pages/ScenarioCatalog';
import { CompareView } from './pages/CompareView';
import { LaunchModal } from './components/LaunchModal';
import { api } from './api/client';
import type { RunConfig, RunSummary, Scenario } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'heatmap' | 'scenarios' | 'compare'>('dashboard');
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRun, setSelectedRun] = useState<RunSummary | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [isLaunchModalOpen, setIsLaunchModalOpen] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);

  useEffect(() => {
    // Initial fetch of scenarios and runs
    api.listScenarios()
      .then(setScenarios)
      .catch((err) => console.warn('Failed to load scenarios:', err));

    api.listRuns()
      .then(async (runList) => {
        if (runList.length > 0) {
          // Fetch full summary of the latest run
          const latest = await api.getRun(runList[0].run_id);
          setSelectedRun(latest);
          setRuns([latest]);
        }
      })
      .catch((err) => console.warn('Failed to list runs:', err));
  }, []);

  const handleLaunchAssessment = async (config: RunConfig) => {
    setIsEvaluating(true);
    try {
      const newSummary = await api.createRun(config);
      setSelectedRun(newSummary);
      setRuns((prev) => [newSummary, ...prev]);
      setIsLaunchModalOpen(false);
      setActiveTab('dashboard');
    } catch (err: any) {
      alert(`Assessment failed: ${err.message}`);
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--vt-bg-app)] text-[var(--vt-text-main)] flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onLaunchClick={() => setIsLaunchModalOpen(true)}
        isEvaluating={isEvaluating}
      />

      <main className="flex-1">
        {activeTab === 'dashboard' && (
          <RunDashboard
            summary={selectedRun}
            onLaunchNew={() => setIsLaunchModalOpen(true)}
          />
        )}

        {activeTab === 'heatmap' && (
          <HeatmapView
            categories={selectedRun?.category_scores || []}
          />
        )}

        {activeTab === 'scenarios' && (
          <ScenarioCatalog scenarios={scenarios} />
        )}

        {activeTab === 'compare' && (
          <CompareView runs={runs} />
        )}
      </main>

      <LaunchModal
        isOpen={isLaunchModalOpen}
        onClose={() => setIsLaunchModalOpen(false)}
        onLaunch={handleLaunchAssessment}
        isLaunching={isEvaluating}
      />
    </div>
  );
};

export default App;
