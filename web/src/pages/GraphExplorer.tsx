import React, { useState } from 'react';
import { Network, Layers, CircleDot } from 'lucide-react';
import type { GraphData, GraphNode } from '../types';
import { NetworkGraph } from '../components/NetworkGraph';

interface GraphExplorerProps {
  graphData: GraphData;
  onInspectEntity: (entityId: string) => void;
  loading: boolean;
}

export const GraphExplorer: React.FC<GraphExplorerProps> = ({
  graphData,
  onInspectEntity,
  loading,
}) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  return (
    <div className="space-y-6">
      {/* Header Deck */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-vantage-700 pb-4 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Network className="w-5 h-5 text-vantage-accent" aria-hidden="true" />
            <h1 className="text-xl font-bold text-white tracking-tight">
              Cross-platform co-occurrence matrix
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Topological relationships, community clusters (Louvain modularity), and betweenness centralities.
          </p>
        </div>

        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="flex items-center space-x-1.5 bg-vantage-900 border border-vantage-700 px-3 py-1.5 rounded">
            <CircleDot className="w-3.5 h-3.5 text-vantage-accent" aria-hidden="true" />
            <span>{graphData.nodes.length} nodes</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-vantage-900 border border-vantage-700 px-3 py-1.5 rounded">
            <Layers className="w-3.5 h-3.5 text-purple-400" aria-hidden="true" />
            <span>{graphData.communities.length} clusters</span>
          </div>
        </div>
      </div>

      {/* Main Interactive Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          {loading ? (
            <div className="h-[520px] flex items-center justify-center text-xs text-slate-500 bg-vantage-950 border border-vantage-700 rounded">
              Calculating topology and centralities...
            </div>
          ) : (
            <NetworkGraph
              data={graphData}
              onSelectNode={(node) => setSelectedNode(node)}
              selectedNodeId={selectedNode?.id}
            />
          )}
        </div>

        {/* Node Inspector Panel */}
        <div className="space-y-4">
          <div className="bg-vantage-900 border border-vantage-700 rounded p-4">
            <h3 className="text-xs font-semibold text-white mb-3">
              Node inspector
            </h3>

            {selectedNode ? (
              <div className="space-y-3 text-xs">
                <div>
                  <div className="text-xs text-slate-500">Entity name</div>
                  <div className="font-mono font-semibold text-vantage-accent break-all mt-0.5">
                    {selectedNode.name}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-vantage-700/60">
                  <div>
                    <div className="text-xs text-slate-500">Type</div>
                    <div className="text-slate-200 capitalize mt-0.5">{selectedNode.entity_type}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Cluster</div>
                    <div className="text-slate-200 mt-0.5">Cluster {selectedNode.community_id}</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-vantage-700/60 font-mono">
                  <div>
                    <div className="text-xs text-slate-500 font-sans">Degree</div>
                    <div className="text-slate-200 mt-0.5">{selectedNode.degree} links</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 font-sans">Betweenness</div>
                    <div className="text-slate-200 mt-0.5">{selectedNode.betweenness.toFixed(4)}</div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => onInspectEntity(selectedNode.id)}
                  className="w-full mt-3 px-3 py-2 bg-vantage-accent text-white rounded text-xs font-medium hover:bg-blue-600 transition-colors text-center"
                >
                  Open entity trajectory
                </button>
              </div>
            ) : (
              <div className="text-xs text-slate-500 py-8 text-center">
                Click any node on the graph canvas to inspect topological metrics.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
