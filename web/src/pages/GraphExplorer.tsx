import React, { useState } from 'react';
import { Network, Search, Layers, CircleDot } from 'lucide-react';
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-vantage-800 pb-4 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Network className="w-5 h-5 text-vantage-accent" />
            <h1 className="text-xl font-mono font-bold text-white tracking-wide">
              CROSS-PLATFORM CO-OCCURRENCE MATRIX
            </h1>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Visualizing topological relationships, community clusters (Louvain greedy modularity), and betweenness centrality.
          </p>
        </div>

        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="flex items-center space-x-1.5 bg-vantage-900 border border-vantage-800 px-3 py-1.5 rounded">
            <CircleDot className="w-3.5 h-3.5 text-vantage-accent" />
            <span>{graphData.nodes.length} Nodes</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-vantage-900 border border-vantage-800 px-3 py-1.5 rounded">
            <Layers className="w-3.5 h-3.5 text-vantage-neon" />
            <span>{graphData.communities.length} Clusters</span>
          </div>
        </div>
      </div>

      {/* Main Interactive Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          {loading ? (
            <div className="h-[520px] flex items-center justify-center text-xs font-mono text-slate-500 bg-vantage-950 border border-vantage-800 rounded-lg">
              CALCULATING TOPOLOGY & CENTRALITIES...
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
          <div className="bg-vantage-900 border border-vantage-700 rounded-lg p-4">
            <h3 className="font-mono text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center space-x-1.5">
              <span>NODE INSPECTOR</span>
            </h3>

            {selectedNode ? (
              <div className="space-y-3 font-mono text-xs">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase">Entity Name</div>
                  <div className="text-sm font-bold text-vantage-accent break-all mt-0.5">
                    {selectedNode.name}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-vantage-800">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Type</div>
                    <div className="text-slate-200 capitalize mt-0.5">{selectedNode.entity_type}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Cluster</div>
                    <div className="text-slate-200 mt-0.5">#{selectedNode.community_id}</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-vantage-800">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Degree</div>
                    <div className="text-slate-200 mt-0.5">{selectedNode.degree} links</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Betweenness</div>
                    <div className="text-slate-200 mt-0.5">{selectedNode.betweenness.toFixed(4)}</div>
                  </div>
                </div>

                <button
                  onClick={() => onInspectEntity(selectedNode.id)}
                  className="w-full mt-3 px-3 py-2 bg-vantage-accent/20 hover:bg-vantage-accent/30 text-vantage-accent border border-vantage-accent/40 rounded text-xs font-bold transition-all text-center"
                >
                  OPEN ENTITY TRAJECTORY
                </button>
              </div>
            ) : (
              <div className="text-xs text-slate-500 font-mono py-8 text-center">
                Click any node on the graph canvas to inspect topological metrics.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
