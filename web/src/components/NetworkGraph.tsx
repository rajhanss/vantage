import React, { useEffect, useRef, useState } from 'react';
import type { GraphData, GraphNode } from '../types';

interface NetworkGraphProps {
  data: GraphData;
  onSelectNode: (node: GraphNode) => void;
  selectedNodeId?: string;
}

const TYPE_COLORS: Record<string, string> = {
  repository: '#00f0ff',
  model: '#a371f7',
  package: '#00ff66',
  paper: '#f0883e',
  topic: '#58a6ff',
  community: '#ff7b72',
  author: '#d2a8ff',
};

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  data,
  onSelectNode,
  selectedNodeId,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });
  const [positions, setPositions] = useState<Map<string, { x: number; y: number }>>(new Map());

  // Handle resize
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDimensions({
          width: Math.max(400, entry.contentRect.width),
          height: Math.max(400, entry.contentRect.height),
        });
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  // Compute layout (radial / cluster layout with relaxation)
  useEffect(() => {
    if (!data.nodes.length) return;
    const { width, height } = dimensions;
    const cx = width / 2;
    const cy = height / 2;
    const newPos = new Map<string, { x: number; y: number }>();

    // Position communities in a circle, and nodes around community center
    const communityCount = Math.max(1, data.communities.length);
    const commRadius = Math.min(width, height) * 0.32;

    const commCenters: Array<{ x: number; y: number }> = [];
    for (let c = 0; c < communityCount; c++) {
      const angle = (c / communityCount) * 2 * Math.PI - Math.PI / 2;
      commCenters.push({
        x: cx + commRadius * Math.cos(angle),
        y: cy + commRadius * Math.sin(angle),
      });
    }

    // Group nodes by community
    const byCommunity = new Map<number, GraphNode[]>();
    data.nodes.forEach((n) => {
      const list = byCommunity.get(n.community_id) || [];
      list.push(n);
      byCommunity.set(n.community_id, list);
    });

    byCommunity.forEach((nodes, commId) => {
      const center = commCenters[commId % commCenters.length] || { x: cx, y: cy };
      const subRadius = Math.min(70, 20 + nodes.length * 8);

      nodes.forEach((n, idx) => {
        const angle = (idx / nodes.length) * 2 * Math.PI;
        // Jitter slightly for natural feel
        const r = subRadius * (0.4 + 0.6 * ((idx % 3) / 2));
        newPos.set(n.id, {
          x: Math.max(30, Math.min(width - 30, center.x + r * Math.cos(angle))),
          y: Math.max(30, Math.min(height - 30, center.y + r * Math.sin(angle))),
        });
      });
    });

    setPositions(newPos);
  }, [data, dimensions]);

  return (
    <div ref={containerRef} className="relative w-full h-[520px] bg-vantage-950 border border-vantage-800 rounded-lg overflow-hidden">
      {/* Legend Header */}
      <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-2 text-[10px] font-mono bg-vantage-900/80 backdrop-blur p-2 rounded border border-vantage-800">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-slate-300 capitalize">{type}</span>
          </div>
        ))}
      </div>

      <svg width={dimensions.width} height={dimensions.height} className="w-full h-full select-none">
        {/* Graph Edges */}
        <g stroke="#21262d" strokeOpacity={0.6} strokeWidth={1}>
          {data.edges.map((edge, idx) => {
            const p1 = positions.get(edge.source);
            const p2 = positions.get(edge.target);
            if (!p1 || !p2) return null;
            return (
              <line
                key={`edge-${idx}`}
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke={edge.weight > 1 ? '#30363d' : '#21262d'}
                strokeWidth={Math.min(3, 0.5 + edge.weight * 0.5)}
              />
            );
          })}
        </g>

        {/* Graph Nodes */}
        <g>
          {data.nodes.map((node) => {
            const pos = positions.get(node.id);
            if (!pos) return null;
            const isSelected = selectedNodeId === node.id;
            const color = TYPE_COLORS[node.entity_type] || '#58a6ff';
            const radius = Math.min(12, Math.max(5, 4 + node.degree * 1.5));

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={() => onSelectNode(node)}
                className="cursor-pointer transition-transform group"
              >
                {/* Selection ring */}
                {isSelected && (
                  <circle
                    r={radius + 5}
                    fill="none"
                    stroke="#00f0ff"
                    strokeWidth={2}
                    className="animate-pulse"
                  />
                )}
                <circle
                  r={radius}
                  fill={color}
                  fillOpacity={isSelected ? 1.0 : 0.85}
                  stroke="#0d1117"
                  strokeWidth={2}
                  className="hover:scale-125 transition-transform"
                />
                {/* Node Label on hover or selected */}
                <text
                  y={-radius - 4}
                  textAnchor="middle"
                  className={`text-[9px] font-mono fill-slate-300 pointer-events-none transition-opacity ${
                    isSelected ? 'opacity-100 font-bold fill-vantage-accent' : 'opacity-0 group-hover:opacity-100'
                  }`}
                >
                  {node.name.length > 18 ? `${node.name.slice(0, 18)}…` : node.name}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
};
