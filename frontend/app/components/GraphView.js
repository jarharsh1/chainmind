"use client";
import dynamic from "next/dynamic";
import { NODE_COLORS } from "../lib/constants";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

function Legend() {
  return (
    <div className="absolute bottom-4 left-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-700 rounded-lg p-3">
      <div className="grid grid-cols-5 gap-3">
        {Object.entries(NODE_COLORS).map(([label, color]) => (
          <div key={label} className="flex items-center gap-1.5 text-xs">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-slate-400">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Force-directed graph canvas + legend + truncation banner.
export default function GraphView({ graphData, onNodeClick, selectedNodeId, truncated, graphRef }) {
  const drawNode = (node, ctx, globalScale) => {
    const label = node.name || node.id;
    const size = 6;
    if (selectedNodeId === node.id) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, size + 3, 0, 2 * Math.PI);
      ctx.fillStyle = "rgba(56, 189, 248, 0.35)";
      ctx.fill();
    }
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = NODE_COLORS[node.label] || "#666";
    ctx.fill();

    if (globalScale > 0.8) {
      const fontSize = Math.max(10 / globalScale, 2);
      ctx.font = `${fontSize}px Sans-Serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = "#e2e8f0";
      const short = label.length > 18 ? `${label.slice(0, 16)}..` : label;
      ctx.fillText(short, node.x, node.y + size + 2);
    }
  };

  return (
    <div className="absolute inset-0 pt-14">
      {truncated && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-10 text-xs text-amber-300 bg-amber-950/70 border border-amber-800 rounded-full px-3 py-1">
          Showing a capped subset of the graph
        </div>
      )}
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        nodeId="id"
        nodeLabel="name"
        nodeColor={(node) => NODE_COLORS[node.label] || "#666"}
        nodeRelSize={6}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        linkColor={() => "#334155"}
        linkLabel={(link) => link.type}
        onNodeClick={onNodeClick}
        backgroundColor="#030712"
        nodeCanvasObject={drawNode}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.beginPath();
          ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();
        }}
      />
      <Legend />
    </div>
  );
}
