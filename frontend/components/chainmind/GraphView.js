"use client";
import dynamic from "next/dynamic";
import { Focus, Minus, Plus, ScanSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  KIND_COLORS,
  LABEL_COLOR,
  LINK_COLOR,
  isRiskNode,
  kindFromLabel,
} from "@/lib/constants";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

export function GraphView({ graphData, selected, onSelect, truncated, evidence, graphRef }) {
  const drawNode = (node, ctx, scale) => {
    const color = KIND_COLORS[kindFromLabel(node.label)] || "#6d7f99";
    const size = 7;
    if (isRiskNode(node)) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, size + 8, 0, 2 * Math.PI);
      ctx.fillStyle = "rgba(213, 92, 68, 0.28)";
      ctx.fill();
    }
    ctx.beginPath();
    ctx.roundRect(node.x - size, node.y - size, size * 2, size * 2, 3);
    ctx.fillStyle = color;
    ctx.fill();
    if (selected?.id === node.id) {
      ctx.lineWidth = 2;
      ctx.strokeStyle = "#e6edf5";
      ctx.stroke();
    }
    if (scale > 0.7) {
      const label = node.name || node.id;
      const fontSize = Math.max(10 / scale, 3);
      ctx.font = `${fontSize}px "IBM Plex Mono", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = LABEL_COLOR;
      const short = label.length > 20 ? `${label.slice(0, 18)}…` : label;
      ctx.fillText(short, node.x, node.y + size + 3);
    }
  };

  const zoomBy = (factor) => {
    const g = graphRef.current;
    if (g) g.zoom(g.zoom() * factor, 300);
  };

  return (
    <main className="blueprint relative min-h-[520px] flex-1 overflow-hidden">
      <div className="graph-toolbar left-4 top-4">
        <span className="size-1.5 rounded-full bg-component" />
        <span className="text-muted-foreground">Showing {graphData.nodes.length} nodes</span>
        {truncated && <b className="text-risk">truncated</b>}
      </div>
      <div className="graph-toolbar right-4 top-4 hidden text-muted-foreground sm:flex">
        <ScanSearch />
        force-directed · evidence view
      </div>

      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        nodeId="id"
        nodeLabel="name"
        nodeColor={(node) => KIND_COLORS[kindFromLabel(node.label)] || "#6d7f99"}
        nodeRelSize={7}
        linkColor={() => LINK_COLOR}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        linkLabel={(link) => link.type}
        onNodeClick={onSelect}
        backgroundColor="rgba(0,0,0,0)"
        nodeCanvasObject={drawNode}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.beginPath();
          ctx.roundRect(node.x - 8, node.y - 8, 16, 16, 3);
          ctx.fillStyle = color;
          ctx.fill();
        }}
      />

      <div className="absolute bottom-4 left-4 z-20 flex gap-1">
        <Button variant="outline" size="icon" aria-label="Zoom in" onClick={() => zoomBy(1.4)}>
          <Plus />
        </Button>
        <Button variant="outline" size="icon" aria-label="Zoom out" onClick={() => zoomBy(0.7)}>
          <Minus />
        </Button>
        <Button
          variant="outline"
          size="icon"
          aria-label="Fit graph"
          onClick={() => graphRef.current?.zoomToFit(400, 50)}
        >
          <Focus />
        </Button>
      </div>

      {evidence && (
        <div className="graph-evidence z-20">
          <b className="font-mono text-risk">EVIDENCE</b>
          <p className="mt-1 text-muted-foreground">{evidence}</p>
        </div>
      )}
    </main>
  );
}
