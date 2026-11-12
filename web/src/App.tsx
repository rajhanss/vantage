import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import type {
  GraphData,
  InvestigationDossier,
  PlatformStats,
  Recommendation,
  Signal,
  TrendDetail,
} from './types';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { TrendsPage } from './pages/TrendsPage';
import { GraphExplorer } from './pages/GraphExplorer';
import { InvestigationView } from './pages/InvestigationView';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('signals');
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [trends, setTrends] = useState<TrendDetail[]>([]);
  const [selectedTrend, setSelectedTrend] = useState<TrendDetail | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [], communities: [] });
  const [dossiers, setDossiers] = useState<InvestigationDossier[]>([]);
  const [selectedDossier, setSelectedDossier] = useState<InvestigationDossier | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [ingestRunning, setIngestRunning] = useState<boolean>(false);
  const [investigating, setInvestigating] = useState<boolean>(false);
  const [notice, setNotice] = useState<string>('');

  const showNotice = (msg: string) => {
    setNotice(msg);
    setTimeout(() => setNotice(''), 4000);
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsRes, signalsRes, trendsRes, graphRes, dossiersRes] = await Promise.allSettled([
        api.getStats(),
        api.getSignals(0.0, 50),
        api.getTrends(40),
        api.getGraph(150),
        api.getInvestigations(20),
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value);
      if (signalsRes.status === 'fulfilled') setSignals(signalsRes.value);
      if (trendsRes.status === 'fulfilled') {
        setTrends(trendsRes.value);
        if (trendsRes.value.length > 0 && !selectedTrend) {
          setSelectedTrend(trendsRes.value[0]);
          loadRecommendations(trendsRes.value[0].entity.id);
        }
      }
      if (graphRes.status === 'fulfilled') setGraphData(graphRes.value);
      if (dossiersRes.status === 'fulfilled') {
        setDossiers(dossiersRes.value);
        if (dossiersRes.value.length > 0 && !selectedDossier) {
          setSelectedDossier(dossiersRes.value[0]);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async (entityId: string) => {
    try {
      const recs = await api.getRecommendations(entityId, 8);
      setRecommendations(recs);
    } catch {
      setRecommendations([]);
    }
  };

  useEffect(() => {
    loadData();
    const timer = setInterval(async () => {
      try {
        const s = await api.getIngestStatus();
        setIngestRunning(s.running);
      } catch {
        // ignore
      }
    }, 8000);
    return () => clearInterval(timer);
  }, []);

  const handleSelectTrend = (t: TrendDetail) => {
    setSelectedTrend(t);
    loadRecommendations(t.entity.id);
  };

  const handleInspectEntity = async (entityId: string) => {
    try {
      const detail = await api.getTrend(entityId);
      setSelectedTrend(detail);
      loadRecommendations(entityId);
      setCurrentTab('trends');
    } catch (e) {
      showNotice(`Entity inspection failed: ${e}`);
    }
  };

  const handleStartInvestigation = async (entityId: string) => {
    try {
      setInvestigating(true);
      showNotice('Investigation agent dispatched...');
      const dossier = await api.startInvestigation(entityId);
      setDossiers((prev) => [dossier, ...prev]);
      setSelectedDossier(dossier);
      setCurrentTab('investigate');
      showNotice('Investigation dossier completed.');
    } catch (e) {
      showNotice(`Investigation failed: ${e}`);
    } finally {
      setInvestigating(false);
    }
  };

  const handleTriggerIngest = async () => {
    try {
      setIngestRunning(true);
      showNotice('Sweeping public ecosystems: GitHub, Hugging Face, PyPI, arXiv, and HackerNews...');
      await api.triggerIngest();
      setTimeout(loadData, 5000);
    } catch (e) {
      showNotice(`Trigger error: ${e}`);
    }
  };

  return (
    <div className="min-h-screen bg-vantage-950 flex flex-col text-slate-100">
      <Navbar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        stats={stats}
        onTriggerIngest={handleTriggerIngest}
        ingestRunning={ingestRunning}
      />

      {/* Ephemeral Notice Toast */}
      {notice && (
        <div className="fixed bottom-6 right-6 z-50 bg-vantage-800 border border-vantage-600 text-white text-xs px-4 py-2.5 rounded shadow-lg flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-vantage-accent motion-safe:animate-pulse" />
          <span>{notice}</span>
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentTab === 'signals' && (
          <Dashboard
            signals={signals}
            topTrends={trends}
            onInspectEntity={handleInspectEntity}
            loading={loading}
          />
        )}

        {currentTab === 'trends' && (
          <TrendsPage
            trends={trends}
            selectedTrend={selectedTrend}
            onSelectTrend={handleSelectTrend}
            recommendations={recommendations}
            onStartInvestigation={handleStartInvestigation}
            investigating={investigating}
          />
        )}

        {currentTab === 'graph' && (
          <GraphExplorer
            graphData={graphData}
            onInspectEntity={handleInspectEntity}
            loading={loading}
          />
        )}

        {currentTab === 'investigate' && (
          <InvestigationView
            dossiers={dossiers}
            selectedDossier={selectedDossier}
            onSelectDossier={setSelectedDossier}
            loading={loading}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-vantage-700 bg-vantage-950 py-4 text-center text-xs text-slate-500">
        Vantage Intelligence Platform: temporal signal discovery and predictive modeling.
      </footer>
    </div>
  );
};
export default App;
